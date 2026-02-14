# AI Conversation API

A **production-grade Secure REST API** for managing AI-powered conversations. Built with **FastAPI**, **Supabase**, and real-time **SSE Streaming**.

## 🚀 Features

- **Authentication**: Secure JWT-based auth using Supabase.
- **Real-time Streaming**: Server-Sent Events (SSE) for token-by-token AI responses.
- **Data Persistence**: Stores conversations, messages, and metadata in Supabase (PostgreSQL).
- **LLM Integration**: Modular design supporting Groq (Llama 3, Mixtral) and easily extensible to OpenAI/Anthropic.
- **Usage Tracking**: Tracks token usage and estimates costs.
- **RESTful Design**: robust CRUD operations for conversations.

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Auth**: Supabase Auth (JWT)
- **Utilities**: `httpx` (Async HTTP), `tiktoken` (Token counting), `pydantic` (Validation).

## 📂 Directory Structure

```
conversation-api/
├── src/
│   ├── auth/           # Auth routes & dependencies
│   ├── config/         # App configuration
│   ├── conversations/  # Conversation management
│   ├── db/             # Database connection
│   ├── llm/            # LLM client & utilities
│   ├── messages/       # Chat logic & Streaming
│   ├── middleware/     # Error handling & logging
│   ├── usage/          # Usage statistics
│   └── main.py         # Application entry point
├── database/           # SQL Schema
├── docs/               # Architecture documentation
├── requirements.txt    # Dependencies
└── .env.example        # Environment variables template
```

## ⚡ Getting Started

### Prerequisites

- Python 3.10 or higher
- A [Supabase](https://supabase.com/) project
- A [Groq](https://console.groq.com/) API Key (or OpenAI)

### Installation

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/your-username/conversation-api.git
    cd conversation-api
    ```

2.  **Create a Virtual Environment**:

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**:
    - Copy `.env.example` to `.env`:
      ```bash
      cp .env.example .env
      ```
    - Open `.env` and fill in your credentials:
      ```ini
      SUPABASE_URL=https://your-project.supabase.co
      SUPABASE_KEY=your-anon-key
      SUPABASE_DB_URL=postgresql://...
      JWT_SECRET_KEY=your-jwt-secret
      GROQ_API_KEY=gsk_...
      ```

5.  **Database Setup**:
    - Go to your Supabase Dashboard -> SQL Editor.
    - Copy the contents of `database/schema.sql`.
    - Run the SQL query to create the necessary tables.

### Running the API

Start the development server:

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Documentation

Interactive API documentation (Swagger UI) is available at:
👉 **http://localhost:8000/docs**

## 🧪 Testing

You can use the provided `tests/verification_script.py` to verify the project structure (requires dev dependencies):

```bash
python tests/verification_script.py
```

## 🔒 Security

- **JWT Validation**: All protected routes require a valid Bearer token.
- **Row Level Security**: The API enforces user ownership checks on all conversation resources.
- **Validation**: Strict Pydantic models for all request bodies.

## 📄 License

MIT
