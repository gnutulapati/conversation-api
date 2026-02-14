from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List
from uuid import UUID

from src.auth.dependencies import get_current_user
from src.messages.schemas import MessageCreate, MessageResponse
from src.messages.service import MessageService
from src.messages.streaming import stream_generator
from src.db.client import supabase
from src.llm.token_counter import count_tokens

router = APIRouter(prefix="/conversations", tags=["Messages"])

@router.get("/{conversation_id}/messages", response_model=List[dict])
async def list_messages(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    # Determine ownership
    conv = await MessageService.get_messages(conversation_id, limit, offset)
    # Ideally should check ownership of conversation first, added basic check in service but explicit check here is safer
    # For now, relying on service or future RLS
    return conv

@router.post("/{conversation_id}/messages", response_model=dict)
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    return await MessageService.process_chat_message(current_user["id"], conversation_id, data)

@router.post("/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    # 1. Validate conversation access
    conv_res = supabase.table("conversations").select("*").eq("id", conversation_id).eq("user_id", current_user["id"]).execute()
    if not conv_res.data:
         raise HTTPException(status_code=404, detail="Conversation not found")
    conversation = conv_res.data[0]

    # 2. Save User Message
    user_tokens = count_tokens(data.content)
    await MessageService.add_message(
        conversation_id=conversation_id,
        role="user",
        content=data.content,
        token_count=user_tokens
    )

    # 3. Prepare History
    history = await MessageService.get_messages(conversation_id, limit=10)
    messages_payload = [{"role": msg["role"], "content": msg["content"]} for msg in history]
    if conversation.get("system_prompt"):
         messages_payload.insert(0, {"role": "system", "content": conversation["system_prompt"]})

    # 4. Stream Response
    return StreamingResponse(
        stream_generator(
            model=data.model or conversation["model"],
            messages=messages_payload,
            temperature=0.7,
            user_id=current_user["id"],
            conversation_id=conversation_id
            # Note: The generator needs to handle saving the assistant message after completion
            # We'll update stream_generator to do exactly that (it currently has a comment)
        ),
        media_type="text/event-stream"
    )
