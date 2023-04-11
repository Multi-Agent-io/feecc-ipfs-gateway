from typing import Any

from fastapi import Depends
from typed_getenv import getenv

from auth.dependencies import authenticate

AUTHENTICATE: bool = getenv("AUTHENTICATE", var_type=bool)


def load_auth_mode() -> list[Any] | None:
    if AUTHENTICATE:
        return [Depends(authenticate)]
    else:
        return None
