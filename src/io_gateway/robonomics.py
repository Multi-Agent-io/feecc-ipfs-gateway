import os
import typing as tp

from loguru import logger
from robonomicsinterface import RobonomicsInterface

DATALOG_ENABLED: bool = bool(os.getenv("ROBONOMICS_ENABLE_DATALOG", False))
ROBONOMICS_ACCOUNT_SEED: str = os.getenv("ROBONOMICS_ACCOUNT_SEED", "")
ROBONOMICS_CLIENT: tp.Optional[RobonomicsInterface] = None

if DATALOG_ENABLED:
    assert ROBONOMICS_ACCOUNT_SEED, "Datalog is enabled, but the seed is missing. Export it to ROBONOMICS_ACCOUNT_SEED."
    ROBONOMICS_CLIENT = RobonomicsInterface(
        seed=ROBONOMICS_ACCOUNT_SEED, remote_ws=os.getenv("ROBONOMICS_SUBSTRATE_NODE_URL")
    )


def post_to_datalog(content: str) -> None:
    """echo provided string to the Robonomics datalog"""
    logger.info(f"Posting data '{content}' to Robonomics datalog")
    assert ROBONOMICS_CLIENT
    txn_hash: str = ROBONOMICS_CLIENT.record_datalog(content)
    logger.info(f"Data '{content}' has been posted to the Robonomics datalog. {txn_hash=}")
