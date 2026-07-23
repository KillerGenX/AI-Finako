from fastapi import Header, HTTPException, Depends
from supabase import Client, create_client
from backend.core.config import settings
from backend.core.database import get_service_supabase
from backend.core.auth import create_supabase_jwt

async def get_current_user_id(x_telegram_id: int = Header(..., description="Telegram User ID dari n8n")) -> str:
    """
    Memvalidasi Telegram ID dengan database dan mengembalikan Supabase UUID (auth.users.id).
    """
    supabase = get_service_supabase()
    
    # Query menggunakan Service Role untuk menembus RLS dan mencari user berdasarkan telegram_id
    response = supabase.table("profiles").select("id").eq("telegram_id", x_telegram_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=401, detail="Akun Telegram belum terdaftar di sistem.")
        
    return response.data[0]["id"]

async def get_user_supabase(user_id: str = Depends(get_current_user_id)) -> Client:
    """
    Mengembalikan Supabase client yang sudah diinjeksi dengan JWT milik user.
    Semua query database yang menggunakan client ini akan terkena filter RLS.
    """
    token = create_supabase_jwt(user_id)
    
    # Buat instance client baru untuk user ini
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    
    # Set header Authorization agar PostgREST membaca identitas user ini
    client.postgrest.auth(token)
    
    return client
