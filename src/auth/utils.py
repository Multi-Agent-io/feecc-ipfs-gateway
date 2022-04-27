from typing import Any
from fastapi import Depends, HTTPException
from auth.dependencies import AUTHENTICATION_MODE, authenticate_analytics, authenticate_noauth, authenticate_workbench


def load_auth_mode() -> Any:
    match AUTHENTICATION_MODE:
        case "noauth":
            AUTH_DEPENDENCY = Depends(authenticate_noauth)
        case "workbench":
            AUTH_DEPENDENCY = Depends(authenticate_workbench)
        case "analytics":
            AUTH_DEPENDENCY = Depends(authenticate_analytics)
        case _:
            raise HTTPException(status_code=500, detail=f"Unknown authentication mode: {AUTHENTICATION_MODE}")
    return AUTH_DEPENDENCY
