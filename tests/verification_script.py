import sys
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock external dependencies BEFORE importing app logic
sys.modules["supabase"] = MagicMock()
sys.modules["gotrue"] = MagicMock()
sys.modules["gotrue.errors"] = MagicMock()

# Mock settings to avoid .env requirement
from src.config.settings import Settings
Settings.SUPABASE_URL = "https://mock.supabase.co"
Settings.SUPABASE_KEY = "mock-key"
Settings.JWT_SECRET_KEY = "mock-secret"
Settings.GROQ_API_KEY = "mock-groq-key"

# Now import app
from src.conversations.schemas import ConversationCreate
from src.messages.schemas import MessageCreate
from src.auth.schemas import UserLogin

async def verify_structure():
    print("Verifying Pydantic Schemas...")
    try:
        c = ConversationCreate(title="Test", model="llama3")
        print("\u2705 ConversationCreate schema valid")
    except Exception as e:
        print(f"\u274C ConversationCreate schema failed: {e}")

    try:
        m = MessageCreate(content="Hello world")
        print("\u2705 MessageCreate schema valid")
    except Exception as e:
        print(f"\u274C MessageCreate schema failed: {e}")

    print("\nVerifying Import Structure...")
    try:
        from src.main import app
        print("\u2705 FastAPI app initialized successfully")
    except Exception as e:
        print(f"\u274C FastAPI app initialization failed: {e}")
        
    print("\nVerification Complete.")

if __name__ == "__main__":
    asyncio.run(verify_structure())
