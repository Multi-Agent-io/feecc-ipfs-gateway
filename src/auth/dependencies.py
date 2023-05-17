from fastapi import HTTPException, Header, status
from loguru import logger
from typed_getenv import getenv

from .database import MongoDbWrapper
from .models import Employee, AnalyticsUser

PRODUCTION_ENVIRONMENT: bool = getenv("PRODUCTION_ENVIRONMENT", var_type=bool, optional=True, default=False)
TESTING_VALUE_WORKBENCH: str = "1111111111"
TESTING_VALUE_ANALYTICS: str = "fake"


async def authenticate(username: str = Header(TESTING_VALUE_ANALYTICS), rfid_card_id: str = Header(TESTING_VALUE_WORKBENCH)) -> AnalyticsUser | Employee:
    try:
        if username:
            if PRODUCTION_ENVIRONMENT and username == TESTING_VALUE_ANALYTICS:
                raise ValueError("Development credentials are not allowed in production environment")
            user = await MongoDbWrapper().get_concrete_analytics_user(username)
            logger.info(f"Authentication passed. {user.username=}.")
            return user
        elif rfid_card_id:
            if PRODUCTION_ENVIRONMENT and rfid_card_id == TESTING_VALUE_WORKBENCH:
                raise ValueError("Development credentials are not allowed in production environment")
            employee = await MongoDbWrapper().get_concrete_employee(rfid_card_id)
            logger.info(f"Authentication passed. {employee.name=}, {employee.rfid_card_id=}.")
            return employee
    except Exception as e:
        message = f"Authentication failed: {e}"
        logger.error(message)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
        )
