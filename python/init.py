#!/usr/bin/env python3

import logging
from _io import TextIOWrapper
import sys


def getLogger(
    level: int = logging.INFO,
    includeThreadName: bool = False,
    mode: str = "stdout",
    stream: TextIOWrapper = None,
) -> logging.Logger:
    if not stream:
        match mode:
            case "stdout":
                stream = sys.stdout
            case "stderr":
                stream = sys.stderr
    logger = logging.getLogger(__name__)
    if includeThreadName:
        formatStr = "[%(asctime)s] [%(levelname)-8s] [%(threadName)-8s]: %(message)s"
    else:
        formatStr = "[%(asctime)s] [%(levelname)-8s]: %(message)s"
    logging.basicConfig(
        # filename=f"{dirLogs}/{core}-{append}.log",
        # filemode="w",
        # encoding="utf-8",
        stream=stream,
        level=level,
        format=formatStr,
        datefmt="%H:%M:%S",
    )
    logger.info("Logger Initialized")
    return logger
