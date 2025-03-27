#!/usr/bin/env python3

import csv
import datetime

import database
import getLogger
import settings

settings.setup()
settings.parser.add_argument("input", default="db-to-csv.csv", nargs="?")
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
)

cur, con = database.openDB(filename=config["dbFileFull"], logger=logger)
res1 = cur.execute("SELECT * FROM works")
out = res1.fetchall()
mainDict = {}
for i in out:
    mainDict[i[0]] = {
        "id": i[0],
        "title": i[1],
        "chaptersCount": i[2],
        "chaptersExpected": i[3],
        "dateLastDownloaded": i[4],
        "dateLastUpdated": i[5],
        "titleOG": i[6],
        "chaptersCountOG": i[7],
        "chaptersExpectedOG": i[8],
        "dateFirstDownloaded": i[9],
        "dateLastEdited": i[10],
    }
with open(settings.args.input, "w") as csvfile:
    writer = csv.DictWriter(
        csvfile,
        fieldnames=(
            "id",
            "title",
            "chaptersCount",
            "chaptersExpected",
            "dateLastDownloaded",
            "dateLastUpdated",
            "titleOG",
            "chaptersCountOG",
            "chaptersExpectedOG",
            "dateFirstDownloaded",
            "dateLastEdited",
        ),
        quoting=csv.QUOTE_NONNUMERIC,
    )
    writer.writeheader()
    for i in mainDict:
        writer.writerow(mainDict[i])
