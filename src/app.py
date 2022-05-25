from __future__ import annotations

import os
import typing as tp
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from typed_getenv import getenv

from auth.dependencies import authenticate
from io_gateway import ipfs, pinata
from io_gateway.dependencies import get_file
from io_gateway.models import GenericResponse, IpfsPublishResponse
from io_gateway.robonomics import post_to_datalog
from logging_config import CONSOLE_LOGGING_CONFIG, FILE_LOGGING_CONFIG

LOCAL_IPFS_ENABLED: bool = getenv("LOCAL_IPFS_ENABLED", var_type=bool, default=False, optional=True)
PINATA_ENABLED: bool = getenv("PINATA_ENABLED", var_type=bool, default=False, optional=True)
DATALOG_ENABLED: bool = getenv("ROBONOMICS_ENABLE_DATALOG", var_type=bool, default=False, optional=True)

assert LOCAL_IPFS_ENABLED or PINATA_ENABLED, "At least one of the options must be enabled"

# apply logging configuration
logger.configure(handlers=[CONSOLE_LOGGING_CONFIG, FILE_LOGGING_CONFIG])

# set up an ASGI app
app = FastAPI(
    title="Feecc IPFS gateway",
    description="A simple IPFS gateway for Feecc QA system",
    dependencies=[Depends(authenticate)],
)


# allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/publish-to-ipfs/by-path", response_model=tp.Union[IpfsPublishResponse, GenericResponse])  # type: ignore
async def publish_file_by_path(
    background_tasks: BackgroundTasks, file: Path = Depends(get_file)
) -> tp.Union[IpfsPublishResponse, GenericResponse]:
    """
    Publish file to IPFS using local node (if enabled by config) and / or pin to Pinata pinning cloud (if enabled by config).

    File is accepted as an absolute path to the desired file on the host machine
    """
    try:
        cid, uri = await publish_file(file, background_tasks)
        message = f"File {file.name} published"
        logger.info(message)
        return IpfsPublishResponse(status=status.HTTP_200_OK, details=message, ipfs_cid=cid, ipfs_link=uri)

    except Exception as e:
        message = f"An error occurred while publishing file to IPFS: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)


@app.post("/publish-to-ipfs/upload-file", response_model=tp.Union[IpfsPublishResponse, GenericResponse])  # type: ignore
async def publish_file_as_upload(
    background_tasks: BackgroundTasks, file_data: UploadFile = File(...)
) -> tp.Union[IpfsPublishResponse, GenericResponse]:
    """
    Publish file to IPFS using local node (if enabled by config) and / or pin to Pinata pinning cloud (if enabled by config).

    File is accepted as an UploadFile (multipart form data)
    """
    try:
        # temporary fix using on disk caching, need to be reworked to work without saving data on the disk
        cache_dir = "cache"
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)

        path = f"{cache_dir}/{file_data.filename}"
        with open(path, "wb") as f:
            f.write(file_data.file.read())

        cid, uri = await publish_file(Path(path), background_tasks)
        message = f"File {file_data.filename} published"
        logger.info(message)
        return IpfsPublishResponse(status=status.HTTP_200_OK, details=message, ipfs_cid=cid, ipfs_link=uri)

    except Exception as e:
        message = f"An error occurred while publishing file to IPFS: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)


async def publish_file(
    file: tp.Union[os.PathLike[tp.AnyStr], tp.IO[bytes]], background_tasks: BackgroundTasks
) -> tp.Tuple[str, str]:
    if LOCAL_IPFS_ENABLED and PINATA_ENABLED:
        cid, uri = ipfs.publish_to_ipfs(file)
        background_tasks.add_task(pinata.pin_file, file)
    elif LOCAL_IPFS_ENABLED:
        cid, uri = ipfs.publish_to_ipfs(file)
    elif PINATA_ENABLED:
        cid, uri = await pinata.pin_file(file)
    else:
        raise ValueError("Both IPFS and Pinata are disabled in config, cannot get CID")

    if DATALOG_ENABLED:
        background_tasks.add_task(post_to_datalog, cid)
        logger.info(f"CID {cid} will be posted to Robonomics datalog in the background.")

    return cid, uri
