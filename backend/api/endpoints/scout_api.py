from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import Client
from backend.api.deps import get_user_supabase, get_current_user_id
from backend.services.scout_service import discover_account

router = APIRouter()

class ScoutRequest(BaseModel):
    domain: str

@router.post("/discover")
async def api_discover_account(
    request: ScoutRequest, 
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_user_supabase)
):
    """
    Endpoint untuk mencari informasi perusahaan dan mengevaluasi peluang secara otomatis.
    """
    try:
        result = await discover_account(request.domain, user_id, supabase)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
