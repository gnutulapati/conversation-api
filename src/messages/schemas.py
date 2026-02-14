from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal
from datetime import datetime
from uuid import UUID

class MessageCreate(BaseModel):
    content: str
    model: Optional[str] = None # Optional override

class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: Literal["user", "assistant", "system"]
    content: str
    token_count: Optional[int]
    model: Optional[str]
    finish_reason: Optional[str]
    latency_ms: Optional[int]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
