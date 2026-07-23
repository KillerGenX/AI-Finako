from fastapi import APIRouter, Depends, HTTPException, Path
from supabase import Client
from backend.api.deps import get_user_supabase, get_current_user_id
from backend.services.scout_service import discover_account
from backend.models.scout_models import QueryRequest, OpportunityUpdate

router = APIRouter()

@router.post("/discover")
async def api_discover_account(
    request: QueryRequest, 
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_user_supabase)
):
    """
    Endpoint untuk mencari informasi perusahaan dan mengevaluasi peluang berdasarkan query generik.
    """
    try:
        result = await discover_account(request.query, user_id, supabase)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/opportunities/{opportunity_id}/status")
async def api_update_opportunity_status(
    update: OpportunityUpdate,
    opportunity_id: str = Path(...),
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_user_supabase)
):
    """
    Endpoint untuk memperbarui status peluang (misal dari Telegram bot saat klik tombol Approve/Reject).
    """
    try:
        # Kita update berdasarkan ID dan pastikan data ini milik user (dijaga oleh RLS, namun eksplisit lebih baik)
        update_data = {"status": update.status}
        if update.reasoning:
            update_data["reasoning"] = update.reasoning
        if update.next_action:
            update_data["next_action"] = update.next_action
            
        res = supabase.table("opportunities").update(update_data).eq("id", opportunity_id).execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Opportunity not found or not owned by you")
            
        return {"status": "success", "data": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
