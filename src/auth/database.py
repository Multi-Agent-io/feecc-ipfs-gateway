import typing as tp

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from typed_getenv import getenv

from .Singleton import SingletonMeta
from .models import Employee, AnalyticsUser

MONGODB_URI: str = getenv("MONGODB_URI", var_type=str)
MONGO_DATABASE_NAME: str = getenv("MONGO_DATABASE_NAME", var_type=str)


class MongoDbWrapper(metaclass=SingletonMeta):
    """A database wrapper implementation for MongoDB"""

    def __init__(self) -> None:
        """connect to database using credentials"""
        logger.info("Connecting to MongoDB")
        mongo_client: AsyncIOMotorClient = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db_name: str = MONGO_DATABASE_NAME
        self._database = mongo_client[db_name]
        self._employee_collection: AsyncIOMotorCollection = self._database["employeeData"]
        self._analytics_users_collection: AsyncIOMotorCollection = self._database["analyticsCredentials"]

        logger.info("Connected to MongoDB")

    @staticmethod
    async def _get_element_by_key(collection_: AsyncIOMotorCollection, key: str, value: str) -> tp.Dict[str, tp.Any]:
        result: tp.Dict[str, tp.Any] = await collection_.find_one({key: value}, {"_id": 0})

        if not result:
            raise ValueError(f"No results found for query '{key}:{value}'")

        return result

    async def get_concrete_employee(self, card_id: str) -> Employee:
        try:
            employee_data = await self._get_element_by_key(self._employee_collection, key="rfid_card_id", value=card_id)
        except ValueError:
            raise ValueError(f"Employee with card id {card_id} not found")

        return Employee(
            name=employee_data["name"],
            position=employee_data["position"],
            rfid_card_id=employee_data["rfid_card_id"],
        )

    async def get_concrete_analytics_user(self, username: str) -> AnalyticsUser:
        try:
            user_data = await self._get_element_by_key(self._analytics_users_collection, key="username", value=username)
        except ValueError:
            raise ValueError(f"User with username {username} not found")

        return AnalyticsUser(
            username=user_data["username"],
            rule_set=user_data["rule_set"],
        )
