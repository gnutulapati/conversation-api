from fastapi import APIRouter, Depends, Query
from typing import List
from src.auth.dependencies import get_current_user
from src.conversations.schemas import ConversationCreate, ConversationResponse, ConversationUpdate
from src.conversations.service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    return await ConversationService.create_conversation(current_user["id"], data)

@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    return await ConversationService.get_conversations(current_user["id"], limit, offset)

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await ConversationService.get_conversation(current_user["id"], conversation_id)

@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    current_user: dict = Depends(get_current_user)
):
    return await ConversationService.update_conversation(current_user["id"], conversation_id, data)

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    return await ConversationService.delete_conversation(current_user["id"], conversation_id)
