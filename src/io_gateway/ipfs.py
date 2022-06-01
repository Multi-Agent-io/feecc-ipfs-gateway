from __future__ import annotations

import os
import typing as tp
from time import sleep

import ipfshttpclient2 as ipfshttpclient
from loguru import logger
from typed_getenv import getenv

LOCAL_IPFS_ENABLED: bool = getenv("LOCAL_IPFS_ENABLED", var_type=bool, default=False, optional=True)
IPFS_GATEWAY_ADDRESS: str = getenv(
    "IPFS_GATEWAY_ADDRESS", var_type=str, default="https://gateway.ipfs.io/ipfs/", optional=True
)


@logger.catch(reraise=True)
def _get_ipfs_client() -> tp.Optional[ipfshttpclient.Client]:

    if not LOCAL_IPFS_ENABLED:
        logger.warning("IPFS capabilities are disabled")
        return None

    retry_delay = 5
    for i in range(5):
        try:
            client = ipfshttpclient.connect()
            logger.info("Successfully connected to the IPFS node")
            return client

        except Exception as e:
            logger.error(f"An error occurred while getting IPFS client: {e}")
            logger.warning(f"Attempt {i + 1} failed. Retrying in {retry_delay} s.")
            sleep(retry_delay)

    logger.warning("Retry attempts count exceeded. Connection to an IPFS node could not be established.")
    return None


IPFS_CLIENT: tp.Optional[ipfshttpclient.Client] = _get_ipfs_client()


@logger.catch(reraise=True)
def publish_to_ipfs(file: tp.Union[os.PathLike[tp.AnyStr], tp.IO[bytes]]) -> tp.Tuple[str, str]:
    """publish file on IPFS"""
    logger.info("Publishing file to IPFS")

    client = IPFS_CLIENT or _get_ipfs_client()
    if client is None:
        raise ConnectionError("Connection to IPFS node failed, cannot publish file")

    result = client.add(file)
    ipfs_hash: str = result["Hash"]
    ipfs_link: str = IPFS_GATEWAY_ADDRESS + ipfs_hash
    logger.info(f"File published to IPFS, hash: {ipfs_hash}")
    return ipfs_hash, ipfs_link
