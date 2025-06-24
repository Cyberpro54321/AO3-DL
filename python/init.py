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


def init(
    json: str = "",
    dryRun: bool = False,
) -> None:
    global args
    global config
    global logger
    global errLogger
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--infile",
        "-i",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
    )
    parser.add_argument(
        "--outfile",
        "-o",
        nargs="?",
        type=argparse.FileType("w"),
        default=sys.stdout,
    )
    parser.add_argument(
        "--errfile",
        "-e",
        nargs="?",
        type=argparse.FileType("w"),
        default=sys.stderr,
    )
    if json:
        parser.add_argument(
            "--json",
            "-j",
            nargs=1,
            type=argparse.FileType(json),
            help="JSON file containing a whitelist and/or blacklist of works to include.",
        )
    if dryRun:
        parser.add_argument(
            "--dry-run",
            "-d",
            action="store_true",
            help="Perform a 'dry run' without downloading any files or saving anything to local storage.",
        )
    parser.add_argument("--log-level", "-l", default="")
    args = parser.parse_args()

    ini = configparser.ConfigParser()
    ini.read(
        [
            "/etc/ao3-dl/config.ini",
            os.path.expanduser("~/.config/ao3-dl/config.ini"),
            os.path.join(os.path.dirname(__file__), "config.ini"),
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
    config["ao3UsernameFile"] = os.path.expanduser(
        ini.get(
            "ao3", "usernameFile", fallback="~/Documents/AO3-DL/secrets/username.secret"
        )
    )
    config["ao3PasswordFile"] = os.path.expanduser(
        ini.get(
            "ao3", "passwordFile", fallback="~/Documents/AO3-DL/secrets/password.secret"
        )
    )
    config["ao3SessionPickle"] = os.path.expanduser(
        ini.get("ao3", "pickle", fallback="~/Documents/AO3-DL/secrets/session.pickle")
    )
    config["ao3DoLogin"] = ini.getboolean("ao3", "login", fallback=False)
    config["ao3DoLoginAlways"] = ini.getboolean("ao3", "loginAlways", fallback=False)
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


def parseInfile(infile, errLogger: logging.Logger) -> set:
    out = set(())
    for lineRaw in infile:
        line = str(lineRaw).split("#")[0].strip()
        if line:
            out.add(line)
    return out
