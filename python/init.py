import argparse
import configparser
import logging
import os.path
from _io import TextIOWrapper
import sys


def getLogger(
    level: int = logging.INFO,
    includeThreadName: bool = True,
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
        stream=stream,
        level=level,
        format=formatStr,
        datefmt="%H:%M:%S",
    )
    if stream != sys.stderr:
        logger.info("Logger Initialized")
    return logger


parser = argparse.ArgumentParser()
parser.add_argument(
    "--infile", "-i", nargs="?", type=argparse.FileType("r"), default=sys.stdin
)
parser.add_argument(
    "--outfile", "-o", nargs="?", type=argparse.FileType("w"), default=sys.stdout
)
parser.add_argument(
    "--errfile", "-e", nargs="?", type=argparse.FileType("w"), default=sys.stderr
)
parser.add_argument("--log-level", "-l", default="")
args = parser.parse_args()

ini = configparser.ConfigParser()
ini.read(
    [
        "/etc/ao3-dl/config.ini",
        os.path.expanduser("~/.config/ao3-dl/config.ini"),
        "config.ini",
    ]
)
config = {}
config["dirRaws"] = os.path.expanduser(
    ini.get("dir", "raws", fallback="~/Documents/AO3-DL/Raws/")
)
config["dirOut"] = os.path.expanduser(
    ini.get("dir", "out", fallback="~/Documents/AO3-DL/Output/")
)
config["sqlType"] = ini.get("db", "type", fallback="sqlite")
config["sqlLocation"] = ini.get("db", "location", fallback="main.sqlite")
logLevelRaw = ini.get("logs", "level", fallback="")
logLevel = logging.INFO
if args.log_level:
    logLevelRaw = args.log_level
if logLevelRaw:
    try:
        logLevel = int(logLevelRaw)
    except ValueError:
        for i in (
            ("d", logging.DEBUG),
            ("i", logging.INFO),
            ("w", logging.WARNING),
            ("e", logging.ERROR),
            ("c", logging.CRITICAL),
        ):
            if str(logLevelRaw)[:1].lower() == i[0]:
                logLevel = i[1]
logger = getLogger(level=logLevel, stream=args.outfile)
errLogger = getLogger(level=logLevel, stream=args.errfile)
