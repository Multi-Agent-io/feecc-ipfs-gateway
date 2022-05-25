import typing as tp

from loguru import logger
from robonomicsinterface import Account, Datalog
from typed_getenv import getenv

DATALOG_ENABLED: bool = getenv("ROBONOMICS_ENABLE_DATALOG", var_type=bool, default=False)
ROBONOMICS_ACCOUNT: tp.Optional[Account] = None
DATALOG_CLIENT: tp.Optional[Datalog] = None

if DATALOG_ENABLED:
    ROBONOMICS_ACCOUNT = Account(seed=getenv("ROBONOMICS_ACCOUNT_SEED", var_type=str))
    DATALOG_CLIENT = Datalog(
        account=ROBONOMICS_ACCOUNT,
        wait_for_inclusion=False,
    )


def post_to_datalog(content: str) -> None:
    """echo provided string to the Robonomics datalog"""
    logger.info(f"Posting data '{content}' to Robonomics datalog")
    assert DATALOG_CLIENT
    txn_hash: str = DATALOG_CLIENT.record(content)
    logger.info(f"Data '{content}' has been posted to the Robonomics datalog. {txn_hash=}")
