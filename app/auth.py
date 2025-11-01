from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os

security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.environ.get("BOT_USERNAME")
    correct_password = os.environ.get("BOT_PASSWORD")
    if not (
        credentials.username == correct_username
        and credentials.password == correct_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong credentials",
        )
    return credentials
