#!/usr/bin/env python3

import datetime

import database
import getLogger
import settings

settings.setup()
settings.parser.add_argument("input", default="db-to-batch.txt", nargs="?")
settings.parse()
config = settings.settings

logCore = "db-to-csv"
if config["logsTimestamp"]:
    logAppend = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
else:
    logAppend = "latest"
logger = getLogger.getLogger(
    core=logCore,
    append=logAppend,
    dirLogs=config["dirLogs"],
    level=config["logsLevel"],
)

ids = database.getWorkIdSet(filename=config["dbFileFull"], logger=logger)

with open(settings.args.input, "w") as out:
    for i in ids:
        out.write(f"{i}\n")
