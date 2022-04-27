import os

from fastapi import Depends, HTTPException, Header, status
from loguru import logger

from .database import MongoDbWrapper
from .models import Employee, AnalyticsUser

AUTHENTICATION_MODE: str = os.getenv("AUTH_MODE", "")
PRODUCTION_ENVIRONMENT: str | bool = os.getenv("PRODUCTION_ENVIRONMENT", False)
TESTING_VALUE_WORKBENCH: str = "1111111111"
TESTING_VALUE_ANALYTICS: str = "fake"


async def authenticate_workbench(rfid_card_id: str = Header(TESTING_VALUE_WORKBENCH)) -> Employee:
    try:
        if not PRODUCTION_ENVIRONMENT and rfid_card_id == TESTING_VALUE_WORKBENCH:
            raise ValueError("Development credentials are not allowed in production environment")
        employee = await MongoDbWrapper().get_concrete_employee(rfid_card_id)
        logger.info(f"Authentication passed. {employee.name=}, {employee.rfid_card_id=}.")
        return employee

    except Exception as e:
        error = f"An error occured: {e}"
        logger.error(error)
        raise HTTPException(status_code=403, detail=error)


async def authenticate_analytics(username: str = Header(TESTING_VALUE_ANALYTICS)) -> AnalyticsUser:
    try:
        if not PRODUCTION_ENVIRONMENT and username == TESTING_VALUE_ANALYTICS:
            raise ValueError("Development credentials are not allowed in production environment")
        user = await MongoDbWrapper().get_concrete_analytics_user(username)
        logger.info(f"Authentication passed. {user.username=}.")
        return user

    except Exception as e:
        error = f"An error occured: {e}"
        logger.error(error)
        raise HTTPException(status_code=403, detail=error)


async def authenticate_noauth() -> None:
    return None
