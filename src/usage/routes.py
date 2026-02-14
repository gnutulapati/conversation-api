from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user
from src.usage.schemas import UsageStats
from src.db.client import supabase
from src.utils.cost_tracker import calculate_cost

router = APIRouter(prefix="/usage", tags=["Usage"])

@router.get("/stats", response_model=UsageStats)
async def get_usage_stats(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    # 1. Total Conversations
    conv_res = supabase.table("conversations").select("id", count="exact").eq("user_id", user_id).execute()
    total_conversations = conv_res.count
    
    # 2. Get all messages for user (via join or direct query if we had user_id on messages, but we don't)
    # So we must query messages for conversations owned by user.
    # Supabase/PostgREST supports nested resource embedding.
    
    # Query: conversations(messages(token_count, model))
    # This might be heavy for a lot of data, but acceptable for this scope.
    # Alternatively, efficient SQL view or RPC would be better in production.
    res = supabase.table("conversations").select("messages(token_count, model, role)").eq("user_id", user_id).execute()
    
    total_messages = 0
    total_tokens = 0
    cost_estimate = 0.0
    models = set()
    
    for conv in res.data:
        msgs = conv.get("messages", [])
        total_messages += len(msgs)
        for msg in msgs:
            tokens = msg.get("token_count", 0)
            model = msg.get("model")
            role = msg.get("role")
            
            total_tokens += tokens
            if model:
                models.add(model)
                # Simple cost estimation logic
                # We need input/output distinction for accurate cost
                # For now, we'll assume a 50/50 split or just apply a flat rate if distinction is lost
                # Improvement: Store input/output tokens separately in DB
                cost_estimate += calculate_cost(model, 0, tokens) # Treating all as output for conservative estimate or similar

    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "total_tokens": total_tokens,
        "cost_estimate_usd": round(cost_estimate, 6),
        "models_used": list(models)
    }

@router.get("/models")
async def list_models(current_user: dict = Depends(get_current_user)):
    # Return available models
    return {
        "models": [
            {"id": "llama3-8b-8192", "provider": "Groq", "name": "Llama 3 8B"},
            {"id": "mixtral-8x7b-32768", "provider": "Groq", "name": "Mixtral 8x7b"},
            {"id": "gemma-7b-it", "provider": "Groq", "name": "Gemma 7B"}
        ]
    }
