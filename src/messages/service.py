import time
from uuid import UUID
from fastapi import HTTPException
from src.db.client import supabase
from src.messages.schemas import MessageCreate
from src.llm.token_counter import count_tokens, count_message_tokens
from src.llm.client import get_llm_client, GroqClient

class MessageService:
    @staticmethod
    async def get_messages(conversation_id: str, limit: int = 50, offset: int = 0):
        response = supabase.table("messages")\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("created_at", desc=False)\
            .range(offset, offset + limit - 1)\
            .execute()
        return response.data

    @staticmethod
    async def add_message(conversation_id: str, role: str, content: str, model: str = None, token_count: int = 0, finish_reason: str = None, latency_ms: int = 0):
        data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "token_count": token_count,
            "model": model,
            "finish_reason": finish_reason,
            "latency_ms": latency_ms
        }
        response = supabase.table("messages").insert(data).execute()
        return response.data[0]

    @staticmethod
    async def process_chat_message(user_id: str, conversation_id: str, data: MessageCreate):
        # 1. Verify ownership/existence
        conv_res = supabase.table("conversations").select("*").eq("id", conversation_id).eq("user_id", user_id).execute()
        if not conv_res.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        conversation = conv_res.data[0]
        
        # 2. Store User Message
        user_tokens = count_tokens(data.content)
        await MessageService.add_message(
            conversation_id=conversation_id,
            role="user",
            content=data.content,
            token_count=user_tokens
        )
        
        # 3. Retrieve Context (History)
        # Simple strategy: last 10 messages for now. Real implementation needs smarter windowing.
        history = await MessageService.get_messages(conversation_id, limit=10)
        messages_payload = [{"role": msg["role"], "content": msg["content"]} for msg in history]
        
        # Add system prompt if exists
        if conversation.get("system_prompt"):
             messages_payload.insert(0, {"role": "system", "content": conversation["system_prompt"]})

        # 4. Call LLM (Non-streaming)
        model = data.model or conversation["model"]
        client = get_llm_client()
        
        start_time = time.time()
        # Non-streaming implementation of calling (since the client only has stream_chat currently, let's adapt)
        # If the client only provided streaming, we'd consume it all. 
        # But usually we'd have a separate acreate/process method. 
        # For now, let's consume the stream to simulate non-streaming.
        full_response = ""
        finish_reason = None
        
        async for chunk in client.stream_chat(messages_payload, model):
            if "error" in chunk:
                raise HTTPException(status_code=502, detail=chunk["error"])
            full_response += chunk.get("content", "")
            if chunk.get("finish_reason"):
                finish_reason = chunk["finish_reason"]
                
        latency = int((time.time() - start_time) * 1000)
        output_tokens = count_tokens(full_response)
        
        # 5. Store Assistant Message
        assistant_msg = await MessageService.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response,
            model=model,
            token_count=output_tokens,
            finish_reason=finish_reason,
            latency_ms=latency
        )
        
        # 6. Auto-title if first user message (simple check: total messages <= 2)
        if len(history) <= 2:
            # Fire and forget title generation could go here
            title_messages = messages_payload + [{"role": "user", "content": "Generate a short 3-5 word title for this conversation."}]
            # Skipping implementation for brevity, but this is where it goes.
            pass

        return assistant_msg
