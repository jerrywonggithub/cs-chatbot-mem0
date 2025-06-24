# Customer Support Chatbot

A full-stack customer support chatbot application using AWS Bedrock and Claude 3.7 Sonnet with memory capabilities powered by Mem0 and OpenSearch.

## Project Structure

```
customer-support-chatbot/
├── backend/               # Flask API server
│   ├── app.py             # Main Flask application
│   ├── support_chatbot.py # Chatbot logic with AWS Bedrock
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Environment variables template
│
└── frontend/              # Web interface
    ├── index.html         # HTML structure
    ├── styles.css         # CSS styling
    └── script.js          # JavaScript for UI interactions
```

## Features

- Memory-powered chatbot that remembers previous conversations
- Vector search for retrieving relevant past interactions
- Clean and responsive chat interface
- AWS Bedrock integration with Claude 3.7 Sonnet
- OpenSearch for vector storage
- User session management

## Prerequisites

- AWS Account with Bedrock access
- AWS CLI configured with appropriate permissions
- Python 3.7+
- Node.js and npm (optional, for serving the frontend)

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd customer-support-chatbot/backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file by copying the template:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file with your AWS and OpenSearch configuration.

6. Run the Flask server:
   ```
   flask run
   ```
   The API will be available at http://localhost:5000

### Frontend Setup

The frontend is a static HTML/CSS/JS application that can be served in several ways:

1. Using a simple HTTP server:
   ```
   cd customer-support-chatbot/frontend
   python -m http.server 8000
   ```
   The website will be available at http://localhost:8000

2. Alternatively, you can use any web server of your choice to serve the static files.

## Usage

1. Open the web interface in your browser.
2. Start asking questions to the customer support chatbot.
3. The chatbot will remember previous conversations and respond accordingly.

## API Endpoints

- `GET /api/health` - Health check endpoint
- `POST /api/chat` - Send a message to the chatbot
  - Request body: `{ "message": "Your message", "user_id": "optional-user-id" }`
  - Response: `{ "response": "Bot's response", "user_id": "user-id" }`
- `GET /api/history?user_id=<user_id>&query=<query>` - Retrieve conversation history

## Notes

- Make sure your AWS CLI is configured with the correct profile that has access to Bedrock and OpenSearch.
- For production use, consider implementing proper authentication and securing the API endpoints.
- The AWS Bedrock models used may incur costs, please check AWS pricing.

## License

[MIT License](LICENSE)
