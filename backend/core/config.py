import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Finako AI"
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    
    TAVILY_API_KEY: str = ""
    FIRECRAWL_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    VERTEX_PROJECT: str = ""
    VERTEX_LOCATION: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
