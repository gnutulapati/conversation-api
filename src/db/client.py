from supabase import create_client, Client
from src.config.settings import settings

def get_supabase_client() -> Client:
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    supabase: Client = create_client(url, key)
    return supabase

# Singleton instance
supabase: Client = get_supabase_client()
