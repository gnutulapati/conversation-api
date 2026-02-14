from src.db.client import supabase
from src.conversations.schemas import ConversationCreate, ConversationUpdate
from fastapi import HTTPException
from uuid import UUID

class ConversationService:
    @staticmethod
    async def create_conversation(user_id: str, data: ConversationCreate):
        response = supabase.table("conversations").insert({
            "user_id": user_id,
            "title": data.title,
            "model": data.model,
            "system_prompt": data.system_prompt,
            "metadata": data.metadata
        }).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create conversation")
        return response.data[0]

    @staticmethod
    async def get_conversations(user_id: str, limit: int = 20, offset: int = 0):
        response = supabase.table("conversations")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("updated_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        return response.data

    @staticmethod
    async def get_conversation(user_id: str, conversation_id: str):
        response = supabase.table("conversations")\
            .select("*")\
            .eq("id", conversation_id)\
            .eq("user_id", user_id)\
            .execute()
            
        if not response.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return response.data[0]

    @staticmethod
    async def update_conversation(user_id: str, conversation_id: str, data: ConversationUpdate):
        update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items()}
        if not update_data:
            return await ConversationService.get_conversation(user_id, conversation_id)

        response = supabase.table("conversations")\
            .update(update_data)\
            .eq("id", conversation_id)\
            .eq("user_id", user_id)\
            .execute()
            
        if not response.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return response.data[0]

    @staticmethod
    async def delete_conversation(user_id: str, conversation_id: str):
        response = supabase.table("conversations")\
            .delete()\
            .eq("id", conversation_id)\
            .eq("user_id", user_id)\
            .execute()
            
        return {"message": "Conversation deleted successfully"}
