from fastapi import APIRouter, Depends, HTTPException
from app.models.admin_model import UserId, UserIds, SetMode
from app.services import AccessControlService
from app.dependencies import get_access_control_service
from app.auth import verify_credentials

router = APIRouter(
    prefix="/admin", tags=["admin"], dependencies=[Depends(verify_credentials)]
)


@router.get("/whitelist", response_model=list[str])
def get_whitelist(service: AccessControlService = Depends(get_access_control_service)):
    return list(service.get_whitelist())


@router.post("/whitelist")
async def add_to_whitelist(
    users: UserIds, service: AccessControlService = Depends(get_access_control_service)
):
    try:
        service.add_to_whitelist(users.user_ids)
        return {"status": "ok", "message": "User(s) added to whitelist"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/whitelist")
def remove_from_whitelist(
    user_id: UserId, service: AccessControlService = Depends(get_access_control_service)
):
    try:
        service.remove_from_whitelist(user_id.user_id)
        return {"status": "ok", "message": "User removed from whitelist"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/blacklist", response_model=list[str])
def get_blacklist(service: AccessControlService = Depends(get_access_control_service)):
    return list(service.get_blacklist())


@router.post("/blacklist")
async def add_to_blacklist(
    users: UserIds, service: AccessControlService = Depends(get_access_control_service)
):
    try:
        service.add_to_blacklist(users.user_ids)
        return {"status": "ok", "message": "User(s) added to blacklist"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/blacklist")
def remove_from_blacklist(
    user_id: UserId, service: AccessControlService = Depends(get_access_control_service)
):
    try:
        service.remove_from_blacklist(user_id.user_id)
        return {"message": "User removed from blacklist"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/mode", response_model=str)
def get_mode(service: AccessControlService = Depends(get_access_control_service)):
    return service.mode.name


@router.post("/mode")
def set_mode(
    mode: SetMode, service: AccessControlService = Depends(get_access_control_service)
):
    try:
        service.set_mode(mode.mode)
        return {"message": f"Mode set to {mode.mode.name}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
