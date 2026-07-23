from supabase import Client, create_client
from backend.core.config import settings
from backend.core.database import get_service_supabase
from backend.core.auth import create_supabase_jwt
from typing import Optional

def authenticate_telegram_user(telegram_id: int) -> Optional[Client]:
    """
    Mencari user berdasarkan Telegram ID. Jika ditemukan, kembalikan instance Supabase
    yang sudah diinjeksi dengan JWT milik user tersebut (sehingga RLS berlaku).
    Jika tidak ditemukan, kembalikan None.
    """
    supabase_service = get_service_supabase()
    
    # Query menggunakan Service Role untuk menembus RLS dan mencari user berdasarkan telegram_id
    response = supabase_service.table("profiles").select("id").eq("telegram_id", telegram_id).execute()
    
    if not response.data:
        return None
        
    user_id = response.data[0]["id"]
    
    # Buat JWT untuk user ini
    token = create_supabase_jwt(user_id)
    
    # Buat client Supabase baru khusus untuk user ini
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    client.postgrest.auth(token)
    
    # Simpan ID user ke dalam client untuk akses mudah (bersifat dinamis di Python)
    client.finako_user_id = user_id
    
    return client
