from __future__ import annotations

import os
import typing as tp
from time import time

import httpx
from loguru import logger
from typed_getenv import getenv

IPFS_GATEWAY_ADDRESS: str = getenv(
    "IPFS_GATEWAY_ADDRESS", default="https://gateway.ipfs.io/ipfs/", optional=True, var_type=str
)
PINATA_ENABLED: bool = getenv("PINATA_ENABLED", default=False, var_type=bool, optional=True)
PINATA_ENDPOINT: str = "https://api.pinata.cloud"
PINATA_API: str = getenv("PINATA_API", var_type=str, default="", optional=True)
PINATA_SECRET_API: str = getenv("PINATA_SECRET_API", default="", var_type=str, optional=True)
AUTH_HEADERS = {"pinata_api_key": PINATA_API, "pinata_secret_api_key": PINATA_SECRET_API}

if PINATA_ENABLED:
    assert PINATA_API and PINATA_SECRET_API, "Pinata credentials are missing"
else:
    logger.warning("Pinata capabilities are disabled")


@logger.catch(reraise=True)
async def pin_file(file: tp.Union[os.PathLike[tp.AnyStr], tp.IO[bytes]]) -> tp.Tuple[str, str]:
    logger.info("Pushing file to Pinata")
    t0 = time()

    files = {"file": open(file, "rb") if isinstance(file, os.PathLike) else file}
    async with httpx.AsyncClient(base_url=PINATA_ENDPOINT, timeout=600.0) as client:
        response = await client.post("/pinning/pinFileToIPFS", files=files, headers=AUTH_HEADERS)

    data = response.json()
    ipfs_hash: str = data["IpfsHash"]
    ipfs_link: str = IPFS_GATEWAY_ADDRESS + ipfs_hash
    logger.info("Published file to Pinata.")
    logger.debug(f"Push took {round(time() - t0, 3)} s.")
    logger.debug(data)
    return ipfs_hash, ipfs_link
