#!/usr/bin/env python3

import argparse
import configparser
import logging
import os.path

import constants


def toAbsPath(input: str):
    return os.path.abspath(os.path.expanduser(input))


def setup():
    global parser
    parser = argparse.ArgumentParser(
        epilog="Options that start with 'Override' have their defaults set in config.ini.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=constants.version,
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.ini",
        help="The config file to use (default: %(default)s)",
        metavar="",
    )
    parser.add_argument(
        "--raws",
        type=str,
        help="Override what directory raw HTML files are expected to be in.",
        metavar="",
    )
    parser.add_argument(
        "--logs",
        "-l",
        type=str,
        help="Override what directory the log file will be written to.",
        metavar="",
    )
    parser.add_argument(
        "--logs-timestamp",
        type=str,
        help="Override whether to use timestamps in log filenames or not.",
        metavar="",
        choices=[
            "False",
            "True",
            "No",
            "Yes",
            "false",
            "true",
            "no",
            "yes",
            "F",
            "T",
            "N",
            "Y",
            "f",
            "t",
            "n",
            "y",
        ],
    )


def input(
    default: str = "",
    helptext: str = "Input",
    name: str = "input",
):
    if default:
        parser.add_argument(
            name,
            type=str,
            default=default,
            help=helptext,
        )
    else:
        parser.add_argument(
            name,
            type=str,
            help=helptext,
        )


def parse():
    global args
    args = parser.parse_args()
    global settings
    settings = {}
    config = configparser.ConfigParser()
    config.read(args.config)

    if args.raws:
        settings["dirRaws"] = toAbsPath(args.raws)
    else:
        settings["dirRaws"] = toAbsPath(config["raws"]["dir"])

    settings["dirOutput"] = toAbsPath(config["output"]["dir"])

    settings["dirOutHtml"] = config["output"]["html"].strip("/")

    settings["dirWorkskins"] = config["output"]["workskins"].strip("/")

    settings["dirOutImg"] = config["output"]["images"].strip("/")

    settings["doImageDownloading"] = config["output"].getboolean("doImageDownloading")

    settings["dirAO3CSS"] = config["output"]["ao3css"].strip("/")

    settings["ao3cssMerged"] = config["ao3"].getboolean("cssMerged")

    settings["dbFileFull"] = toAbsPath(
        f'{settings["dirOutput"]}/{config["output"]["database"]}'
    )

    if args.logs:
        settings["dirLogs"] = toAbsPath(args.logs)
    else:
        settings["dirLogs"] = toAbsPath(config["logs"]["dir"])

    if args.logs_timestamp is None:
        settings["logsTimestamp"] = config["logs"].getboolean("timestamp")
    else:
        if str(args.logs_timestamp).lower()[:1] in ("y", "t"):
            settings["logsTimestamp"] = True
        else:
            settings["logsTimestamp"] = False

    settings["ao3DoLogin"] = config["ao3"].getboolean("login")

    settings["ao3UsernameFile"] = toAbsPath(config["ao3"]["usernameFile"])

    settings["ao3PasswordFile"] = toAbsPath(config["ao3"]["passwordFile"])

    if isinstance(config["logs"]["level"], str):
        for i in (
            ("debug", logging.DEBUG),
            ("info", logging.INFO),
            ("warning", logging.WARNING),
            ("error", logging.ERROR),
            ("critical", logging.CRITICAL),
        ):
            if config["logs"]["level"].lower() == i[0]:
                settings["logsLevel"] = i[1]
    elif isinstance(config["logs"]["level"], int):
        settings["logsLevel"] - config["logs"]["level"]

    for i in ("dirRaws", "dirLogs"):
        if not os.path.exists(settings[i]):
            raise Exception(f"Specified directory doesn't exist: {settings[i]}")
