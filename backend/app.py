from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import traceback
from dotenv import load_dotenv
from support_chatbot import SupportChatbot

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize chatbot
chatbot = SupportChatbot()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle customer queries."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract data from request
        message = data.get('message')
        user_id = data.get('user_id')
        
        # Validate required fields
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Generate a user ID if not provided
        if not user_id:
            user_id = str(uuid.uuid4())

        # Process the customer query
        response = chatbot.handle_customer_query(user_id, message)
        
        # Return the response
        return jsonify({
            "response": response,
            "user_id": user_id
        })

    except Exception as e:
        print(f"Error processing chat request: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Failed to process query", "details": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history for a user."""
    try:
        user_id = request.args.get('user_id')
        query = request.args.get('query', '')
        
        # Validate required fields
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Get relevant history
        history = chatbot.get_relevant_history(user_id, query)
        
        # Return the history
        return jsonify({"history": history})

    except Exception as e:
        print(f"Error retrieving history: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Failed to retrieve history", "details": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
