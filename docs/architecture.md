# AI Conversation API Architecture

## Overview

This project implements a Secure REST API for AI-powered conversations, featuring real-time SSE streaming, Supabase authentication, and a modular design.

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Auth**: Supabase Auth (JWT)
- **LLM**: Groq (Llama 3, Mixtral) via `httpx`
- **Streaming**: Server-Sent Events (SSE)

## Directory Structure

```
src/
├── auth/           # Authentication routes & dependencies
├── config/         # Environment settings
├── conversations/  # Conversation CRUD
├── db/             # Database client
├── llm/            # LLM client & token counting
├── messages/       # Chat logic & Streaming
├── middleware/     # Global error handling
├── usage/          # Usage statistics
├── utils/          # Cost tracking & validators
└── main.py         # Entry point
```

## Key Components

### 1. Authentication

- Uses **Supabase Auth** for user management.
- JWT tokens are verified in `src/auth/dependencies.py` using the project's JWT Secret.
- RLS (Row Level Security) should be enabled in Supabase to strictly enforce data isolation at the database level, though the API also checks ownership in `service.py`.

### 2. Streaming (SSE)

- Located in `src/messages/streaming.py`.
- Yields events in a specific format compatible with Anthropic/OpenAI client libs.
- **Protocol**:
  - `message_start`
  - `content_block_start`
  - `content_block_delta` (streaming tokens)
  - `content_block_stop`
  - `message_stop`
- **Persistence**: The full assistant message is saved to Supabase _after_ the stream completes.

### 3. LLM Abstraction

- `src/llm/client.py` defines a `GroqClient`.
- Easy to extend for OpenAI, Anthropic, or others by subclassing `LLMClient`.

### 4. Database Schema

- `users`: Managed by Supabase Auth (or linked).
- `conversations`: Stores metadata, model settings.
- `messages`: Stores individual chat turns, token counts, latency.

## Setup Instructions

1. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `JWT_SECRET_KEY` (from Supabase Project Settings -> API)
   - `GROQ_API_KEY`

2. **Database**:
   Run the SQL in `database/schema.sql` in your Supabase SQL Editor.

3. **Run**:

   ```bash
   pip install -r requirements.txt
   uvicorn src.main:app --reload
   ```

4. **Docs**:
   Visit `http://localhost:8000/docs` for the interactive Swagger UI.
