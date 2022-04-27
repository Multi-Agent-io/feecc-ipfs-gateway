from pydantic import BaseModel


class Employee(BaseModel):
    rfid_card_id: str
    name: str
    position: str


class AnalyticsUser(BaseModel):
    username: str
    rule_set: list[str]
