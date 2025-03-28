#!/usr/bin/env python3

import argparse
import configparser
import logging
import os.path


def toAbsPath(input: str):
    return os.path.abspath(os.path.expanduser(input))


def setup():
    global parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.ini")


def parse():
    global args
    args = parser.parse_args()
    global settings
    settings = {}
    config = configparser.ConfigParser()
    config.read(args.config)
    settings["dirRaws"] = toAbsPath(config["raws"]["dir"])
    settings["dirOutput"] = toAbsPath(config["output"]["dir"])
    settings["dirOutHtml"] = config["output"]["html"].strip("/")
    settings["dirWorkskins"] = config["output"]["workskins"].strip("/")
    settings["dirOutImg"] = config["output"]["images"].strip("/")
    settings["dirAO3CSS"] = config["output"]["ao3css"].strip("/")
    settings["ao3cssMerged"] = config["ao3"].getboolean("cssMerged")
    settings["dbFileFull"] = toAbsPath(config["database"]["file"])
    settings["dirLogs"] = toAbsPath(config["logs"]["dir"])
    settings["logsTimestamp"] = config["logs"].getboolean("timestamp")
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
