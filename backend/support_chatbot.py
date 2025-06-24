import json
import os
from typing import List, Dict
from datetime import datetime

import boto3
from mem0 import Memory
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupportChatbot:
    def __init__(self):
        # Get configuration from environment variables
        region = os.getenv('AWS_REGION', 'us-west-2')
        profile_name = os.getenv('AWS_PROFILE', 'bedrock')
        host = os.getenv('OPENSEARCH_HOST')
        port = int(os.getenv('OPENSEARCH_PORT', 443))
        llm_model = os.getenv('LLM_MODEL')
        embedding_model = os.getenv('EMBEDDING_MODEL', 'cohere.embed-multilingual-v3')

        # Set up AWS session
        boto3.setup_default_session(profile_name=profile_name)
        credentials = boto3._get_default_session().get_credentials()
        
        # Set up AWS auth for OpenSearch
        awsauth = AWSV4SignerAuth(credentials, region)
        
        # Initialize configuration for Mem0
        self.config = {
            "vector_store": {
                "provider": "opensearch",
                "config": {
                    "collection_name": "mem0",
                    "host": host,
                    "port": port,
                    "http_auth": awsauth,
                    "embedding_model_dims": 1024,
                    "connection_class": RequestsHttpConnection,
                    "pool_maxsize": 20,
                    "use_ssl": True,
                    "verify_certs": True
                }
            },
            "llm": {
                "provider": "aws_bedrock",
                "config": {
                    "model": llm_model,
                    "temperature": 0.01,
                    "max_tokens": 2000,
                    "top_k": 100,
                    "top_p": 0.9
                }
            },
            "embedder": {
                "provider": "aws_bedrock",
                "config": {
                    "model": embedding_model
                }
            }
        }
        
        # Initialize Bedrock client and Memory
        self.client = boto3.client('bedrock-runtime', region_name=region)
        self.memory = Memory.from_config(self.config)

        # Define support context
        self.system_context = """
        You are a helpful customer support agent. Use the following guidelines:
        - Be polite and professional
        - Show empathy for customer issues
        - Reference past interactions when relevant
        - Maintain consistent information across conversations
        - If you're unsure about something, ask for clarification
        - Keep track of open issues and follow-ups
        """

    def store_customer_interaction(self, user_id: str, message: str, response: str, metadata: Dict = None):
        """Store customer interaction in memory."""
        if metadata is None:
            metadata = {}

        # Add timestamp to metadata
        metadata["timestamp"] = datetime.now().isoformat()

        # Format conversation for storage
        conversation = [{"role": "user", "content": message}, {"role": "assistant", "content": response}]

        # Store in Mem0
        self.memory.add(conversation, user_id=user_id, metadata=metadata)

    def get_relevant_history(self, user_id: str, query: str) -> Dict:
        """Retrieve relevant past interactions."""
        return self.memory.search(
            query=query,
            user_id=user_id,
            limit=5,  # Adjust based on needs
        )

    def handle_customer_query(self, user_id: str, query: str) -> str:
        """Process customer query with context from past interactions."""

        # Get relevant past interactions
        relevant_history = self.get_relevant_history(user_id, query)

        # Build context from relevant history
        context = "Previous relevant interactions:\n"
        if relevant_history and 'results' in relevant_history:
            for memory in relevant_history['results']:
                context += f"Customer: {memory.get('memory', '')}\n"
                context += f"Support: {memory.get('memory', '')}\n"
                context += "---\n"
        else:
            context += "No previous interactions found.\n"

        # Prepare prompt with context and current query
        prompt = f"""
        {self.system_context}

        {context}

        Current customer query: {query}

        Provide a helpful response that takes into account any relevant past interactions.
        """

        # Generate response using Bedrock, Claude Sonnet 3.7
        bedrock_response = self.client.invoke_model(
            modelId=os.getenv('LLM_MODEL'),
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                "temperature": 0.01,
            })
        )
        
        # Decode the response body
        response = json.loads(bedrock_response.get('body').read())
        response_text = response['content'][0]['text'] if 'content' in response and response['content'] else "Sorry, I couldn't generate a response at this time."

        # Store interaction
        self.store_customer_interaction(
            user_id=user_id, 
            message=query, 
            response=response_text, 
            metadata={"type": "support_query"}
        )

        return response_text
