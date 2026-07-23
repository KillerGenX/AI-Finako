import jwt
from datetime import datetime, timedelta, timezone
from backend.core.config import settings

def create_supabase_jwt(user_id: str, role: str = "authenticated") -> str:
    """
    Creates a JWT that Supabase will accept and use for RLS.
    This allows FastAPI to act on behalf of the user without needing them to login with a password.
    """
    if not settings.SUPABASE_JWT_SECRET:
        raise ValueError("SUPABASE_JWT_SECRET is not set in environment variables")

    payload = {
        "aud": "authenticated",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "sub": str(user_id),  # This maps to auth.uid() in Supabase RLS
        "role": role,
        "app_metadata": {"provider": "telegram", "providers": ["telegram"]},
        "user_metadata": {},
    }
    
    encoded_jwt = jwt.encode(
        payload, 
        settings.SUPABASE_JWT_SECRET, 
        algorithm="HS256"
    )
    return encoded_jwt
