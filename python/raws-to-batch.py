#!/usr/bin/env python3

import datetime
import os.path

import getLogger
import raws
import settings

settings.setup()
settings.input(
    default="raws-to-batch.txt",
    helptext="Name of output batch file",
    name="output",
)
settings.parse()
config = settings.settings

logCore = "raws-to-batch"
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

ids = set(())
for i in os.listdir(config["dirRaws"]):
    if i[-5:] == ".html":
        id = raws.getWorkIdFromBs4(
            soup=raws.getBs4FromFilename(
                filename=f"{config['dirRaws']}/{i}",
                logger=logger,
            ),
            logger=logger,
        )
        ids.add(id)

with open(settings.args.output, "w") as out:
    for i in ids:
        out.write(f"{i}\n")
