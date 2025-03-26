#!/usr/bin/env python3

import logging


def getLogger(
    core: str,
    append: str,
    dirLogs: str,
    level: int = logging.INFO,
    includeThreadName: bool = False,
):
    logger = logging.getLogger(__name__)
    if includeThreadName:
        formatStr = "[%(asctime)s] [%(levelname)-8s] [%(threadName)-8s]: %(message)s"
    else:
        formatStr = "[%(asctime)s] [%(levelname)-8s]: %(message)s"
    logging.basicConfig(
        filename=f"{dirLogs}/{core}-{append}.log",
        filemode="w",
        encoding="utf-8",
        level=level,
        format=formatStr,
        datefmt="%H:%M:%S",
    )
    return logger
