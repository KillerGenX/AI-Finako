from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
import asyncio
from backend.core.config import settings
from backend.api.deps import get_user_supabase
from backend.api.endpoints import scout_api
from supabase import Client
from backend.bot import create_bot_app
import logging

logger = logging.getLogger(__name__)

# Global reference to the bot app
bot_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_app
    bot_app = create_bot_app()
    if bot_app:
        logger.info("Starting Telegram Bot Polling...")
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling()
        logger.info("Telegram Bot started.")
    
    yield
    
    if bot_app:
        logger.info("Stopping Telegram Bot...")
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()
        logger.info("Telegram Bot stopped.")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

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
