from fastapi import APIRouter, Depends, HTTPException
from app.models.admin_model import UserId, UserIds, SetMode
from app.services import AdminService, ChatbotService
from app.core.dependencies import get_admin_service, get_chatbot_service
from app.core.auth import verify_credentials

router = APIRouter(
    prefix="/admin", tags=["admin"], dependencies=[Depends(verify_credentials)]
)


@router.get("/whitelist", response_model=list[str])
def get_whitelist(service: AdminService = Depends(get_admin_service)):
    return list(service.get_whitelist())


@router.post("/whitelist")
async def add_to_whitelist(
    users: UserIds, service: AdminService = Depends(get_admin_service)
):
    try:
        service.add_to_whitelist(users.user_ids)
        return {"status": "ok", "message": "User(s) added to whitelist"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/whitelist")
def remove_from_whitelist(
    user_id: UserId, service: AdminService = Depends(get_admin_service)
):
    try:
        service.remove_from_whitelist(user_id.user_id)
        return {"status": "ok", "message": "User removed from whitelist"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/blacklist", response_model=list[str])
def get_blacklist(service: AdminService = Depends(get_admin_service)):
    return list(service.get_blacklist())


@router.post("/blacklist")
async def add_to_blacklist(
    users: UserIds, service: AdminService = Depends(get_admin_service)
):
    try:
        service.add_to_blacklist(users.user_ids)
        return {"status": "ok", "message": "User(s) added to blacklist"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/blacklist")
def remove_from_blacklist(
    user_id: UserId, service: AdminService = Depends(get_admin_service)
):
    try:
        service.remove_from_blacklist(user_id.user_id)
        return {"message": "User removed from blacklist"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/mode", response_model=str)
def get_mode(service: AdminService = Depends(get_admin_service)):
    return service.mode.name


@router.post("/mode")
def set_mode(
    mode: SetMode, service: AdminService = Depends(get_admin_service)
):
    try:
        service.set_mode(mode.mode)
        return {"message": f"Mode set to {mode.mode.name}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/session/{user_id}")
def delete_user_session(
    user_id: str, chatbot_service: ChatbotService = Depends(get_chatbot_service)
):
    if user_id not in chatbot_service.user_sessions:
        raise HTTPException(status_code=404, detail=f"Session for user {user_id} not found.")
    
    chatbot_service.delete_session(user_id)
    return {"status": "ok", "message": f"Session for user {user_id} deleted."}
