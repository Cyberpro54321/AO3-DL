#!/usr/bin/env python3

import datetime
import logging
import os.path

import raws
import settings

settings.setup()
settings.parser.add_argument("input", default="raws-to-batch.txt", nargs="?")
settings.parse()
config = settings.settings

logger = logging.getLogger(__name__)
if config["logsTimestamp"]:
    logName = f"raws-to-batch-{datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()}"
else:
    logName = "raws-to-batch-latest"
logging.basicConfig(
    filename=f"{config['dirLogs']}/{logName}.log",
    filemode="w",
    encoding="utf-8",
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)-8s]: %(message)s",
    datefmt="%H:%M:%S",
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

with open(settings.args.input, "w") as out:
    for i in ids:
        out.write(f"{i}\n")
