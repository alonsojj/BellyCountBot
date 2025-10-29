from fastapi import APIRouter, Depends, HTTPException
from ..services.access_control_service import AccessControlService
from ..dependencies import get_access_control_service
from ..models.access_control_model import UserId, UserIds, SetMode

router = APIRouter(prefix="/api/v1/access-control", tags=["Access Control"])


@router.get("/whitelist", response_model=list[str])
def get_whitelist(service: AccessControlService = Depends(get_access_control_service)):
    return list(service.get_whitelist())


@router.post("/whitelist")
def add_to_whitelist(
    user_ids: UserIds,
    service: AccessControlService = Depends(get_access_control_service),
):
    try:
        service.add_to_whitelist(user_ids.user_ids)
        return {"message": "User(s) added to whitelist"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/whitelist")
def remove_from_whitelist(
    user_id: UserId, service: AccessControlService = Depends(get_access_control_service)
):
    try:
        service.remove_from_whitelist(user_id.user_id)
        return {"message": "User removed from whitelist"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/blacklist", response_model=list[str])
def get_blacklist(service: AccessControlService = Depends(get_access_control_service)):
    return list(service.get_blacklist())


@router.post("/blacklist")
def add_to_blacklist(
    user_ids: UserIds,
    service: AccessControlService = Depends(get_access_control_service),
):
    try:
        service.add_to_blacklist(user_ids.user_ids)
        return {"message": "User(s) added to blacklist"}
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
