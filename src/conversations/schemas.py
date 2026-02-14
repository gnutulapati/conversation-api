from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    model: str = "llama3-8b-8192"
    system_prompt: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    system_prompt: Optional[str] = None
    is_archived: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: Optional[str]
    model: str
    system_prompt: Optional[str]
    metadata: Dict[str, Any]
    is_archived: bool
    created_at: datetime
    updated_at: datetime
