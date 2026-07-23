from supabase import create_client, Client
from backend.core.config import settings

def get_supabase_client() -> Client:
    """
    Returns a standard Supabase client with the Anon Key.
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

def get_service_supabase() -> Client:
    """
    Returns a Supabase client with Service Role privileges (bypasses RLS).
    Used for system-level queries like verifying a user's Telegram ID.
    """
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("SUPABASE_SERVICE_ROLE_KEY is not set in environment variables")
        
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
