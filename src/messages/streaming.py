import json
import time
from typing import AsyncGenerator
from src.llm.client import get_llm_client
from src.db.client import supabase

async def stream_generator(
    model: str,
    messages: list,
    temperature: float,
    user_id: str, # For logging or future use
    conversation_id: str,
    db_message_id: str = None # if we want to update the DB row later
) -> AsyncGenerator[str, None]:
    """
    Generates SSE events in the specific format required.
    """
    client = get_llm_client()
    
    # event: message_start
    yield f"event: message_start\n"
    yield f"data: {json.dumps({'type': 'message_start', 'message': {'id': db_message_id, 'role': 'assistant', 'model': model}})}\n\n"
    
    # event: content_block_start
    yield f"event: content_block_start\n"
    yield f"data: {json.dumps({'type': 'content_block_start', 'index': 0, 'content_block': {'type': 'text', 'text': ''}})}\n\n"

    full_content = []
    start_time = time.time()
    
    finish_reason = None
    
    async for chunk in client.stream_chat(messages, model, temperature):
        if "error" in chunk:
            yield f"event: error\n"
            yield f"data: {json.dumps({'type': 'error', 'error': {'type': 'api_error', 'message': chunk['error']}})}\n\n"
            return

        content = chunk.get("content", "")
        if content:
            full_content.append(content)
            # event: content_block_delta
            yield f"event: content_block_delta\n"
            yield f"data: {json.dumps({'type': 'content_block_delta', 'index': 0, 'delta': {'type': 'text_delta', 'text': content}})}\n\n"

        if chunk.get("finish_reason"):
             finish_reason = chunk["finish_reason"]
             # event: content_block_stop
             yield f"event: content_block_stop\n"
             yield f"data: {json.dumps({'type': 'content_block_stop', 'index': 0})}\n\n"
            
             # event: message_delta
             yield f"event: message_delta\n"
             yield f"data: {json.dumps({'type': 'message_delta', 'delta': {'stop_reason': finish_reason}, 'usage': {'output_tokens': 0}})}\n\n" # usage is placeholder until we count
            
             # event: message_stop
             yield f"event: message_stop\n"
             yield f"data: {json.dumps({'type': 'message_stop'})}\n\n"

    # Post-stream: Save to DB
    final_text = "".join(full_content)
    if final_text:
        end_time = time.time()
        latency = int((end_time - start_time) * 1000)
        # Import inside to avoid circular dependency (service imports streaming, streaming imports service)
        from src.llm.token_counter import count_tokens
        output_tokens = count_tokens(final_text)
        
        # We can't import MessageService easily due to circular imports with routes -> service -> streaming
        # So we use the supabase client directly or refactor. Direct DB call is safest here.
        
        data = {
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": final_text,
            "token_count": output_tokens,
            "model": model,
            "finish_reason": finish_reason or "stop",
            "latency_ms": latency
        }
        try:
             supabase.table("messages").insert(data).execute()
        except Exception as e:
             # Log error but don't crash stream (it's done anyway)
             print(f"Failed to save streamed message: {e}")
