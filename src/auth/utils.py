from typing import Any

from fastapi import Depends
from typed_getenv import getenv

from auth.dependencies import authenticate_analytics, authenticate_workbench

AUTHENTICATION_MODE: str = getenv("AUTH_MODE", var_type=str)


def load_auth_mode() -> list[Any] | None:
    match AUTHENTICATION_MODE:
        case "noauth":
            return None
        case "workbench":
            AUTH_DEPENDENCY = [Depends(authenticate_workbench)]
        case "analytics":
            AUTH_DEPENDENCY = [Depends(authenticate_analytics)]
        case _:
            raise ValueError(f"Unknown authentication mode: {AUTHENTICATION_MODE}")
    return AUTH_DEPENDENCY
