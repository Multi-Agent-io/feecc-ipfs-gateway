from __future__ import annotations

import os
import typing as tp
from time import sleep

from loguru import logger
from typed_getenv import getenv
import requests

LOCAL_IPFS_ENABLED: bool = getenv("LOCAL_IPFS_ENABLED", var_type=bool, default=False, optional=True)
IPFS_GATEWAY_ADDRESS: str = getenv(
    "IPFS_GATEWAY_ADDRESS", var_type=str, default="https://gateway.ipfs.io/ipfs/", optional=True
)
LOCAL_IPFS_LIST: str = getenv(
    "LOCAL_IPFS_LIST", \
    var_type=str, \
    default=None, \
    optional=True
)
LOCAL_IPFS_IS_CLUSTER_PEER: bool = getenv("LOCAL_IPFS_IS_CLUSTER_PEER", var_type=bool, default=False, optional=True)

@logger.catch(reraise=True)
def _build_url(mode, protocol, socket, endpoint):
    return f'{protocol}://{socket}{"" if mode else "/api/v0"}{endpoint}'

@logger.catch(reraise=True)
def _check_connection_to_ipfs_cluster_peer(socket, mode=LOCAL_IPFS_IS_CLUSTER_PEER, endpoint='/id'):
    protocol = 'http'
    try:
        url = _build_url(mode, protocol, socket, endpoint)
        if mode:
            response = requests.get(url)
        else:
            response = requests.post(url)
        logger.info(f"The check connection url is: {url}")
    except Exception as e:
            logger.error(f"An error occurred while getting IPFS cluster peer client: {e}")
            logger.error(f"The problem url is : {url}")
    else:
        if response.status_code == requests.codes.ok:
            return True
        else:
            return False

@logger.catch(reraise=True)
def publish_to_ipfs(file: tp.Union[os.PathLike[tp.AnyStr], tp.IO[bytes]]) -> tp.Tuple[str, str]:
    """publish file on IPFS"""
    logger.info("Publishing file to IPFS")
    ipfs_cluster_peer_sockets = set(a.split("/")[2]+":"+a.split("/")[4] for a in tuple(LOCAL_IPFS_LIST.split(",")))
    socket = None
    for s in ipfs_cluster_peer_sockets:
        if _check_connection_to_ipfs_cluster_peer(s):
            socket = s
            break
    try:
        assert socket != None
    except AssertionError:
        logger.error("It seems like there is no alive IPFS CLUSTER peer")
    url = _build_url(LOCAL_IPFS_IS_CLUSTER_PEER, 'http', socket, '/add')
    with open(file, 'rb') as fout:
        files = {'upload_file': fout}
        result = requests.post(url, files=files).json()
    if LOCAL_IPFS_IS_CLUSTER_PEER:    
        ipfs_hash: str = result["cid"]
    else:
        ipfs_hash: str = result["Hash"]
    ipfs_link: str = IPFS_GATEWAY_ADDRESS + ipfs_hash
    logger.info(f"File published to IPFS, hash: {ipfs_hash}")
    return ipfs_hash, ipfs_link