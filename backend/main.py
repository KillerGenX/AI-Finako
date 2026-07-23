from fastapi import FastAPI, Depends
from backend.core.config import settings
from backend.api.deps import get_user_supabase
from backend.api.endpoints import scout_api
from supabase import Client

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(scout_api.router, prefix="/api/scout", tags=["Scout AI"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}

@app.get("/me")
async def get_my_profile(supabase: Client = Depends(get_user_supabase)):
    """
    Endpoint untuk mengetes Opsi 2 (JWT & RLS).
    Jika berhasil, akan mengembalikan data profil milik user tersebut saja.
    """
    response = supabase.table("profiles").select("*").execute()
    return {"profile": response.data}
