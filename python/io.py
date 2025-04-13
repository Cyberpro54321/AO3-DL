#!/usr/bin/env python3

import csv
import datetime
import os.path
import logging

import batch
import database
import getLogger
import network
import raws
import settings


################################################################
# Functions
################################################################

################################
# Input
################################


def rawsToSet(
    dirRaws: str,
    logger: logging.Logger,
) -> set:
    ids = set(())
    for i in os.listdir(dirRaws):
        if i[-5:] == ".html":
            id = raws.getWorkIdFromBs4(
                soup=raws.getBs4FromFilename(
                    filename=f"{dirRaws}/{i}",
                    logger=logger,
                ),
                logger=logger,
            )
            ids.add(id)
    return ids


def dbToDict(
    dbFileFull: str,
    logger: logging.Logger,
) -> dict:
    cur, con = database.openDB(filename=dbFileFull, logger=logger)
    out = cur.execute("SELECT * FROM works").fetchall()
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
    return mainDict


################################
# Output
################################


def setToBatch(
    input: set,
    output: str,
    logger: logging.Logger,
    mode: str = "w",
) -> None:
    with open(output, mode) as out:
        for i in input:
            out.write(f"{i}\n")


def dictToCsv(
    input: dict,
    output: str,
    logger: logging.Logger,
) -> None:
    with open(output, "w") as csvfile:
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
        for i in input:
            writer.writerow(input[i])


################################################################
# Main
################################################################


settings.setup()
group = settings.parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    "--batch-from-raws",
    type=str,
    help="Extract the Work IDs from all files in the Raws directory and write them to a simple batch file.",
    metavar="Output File",
)
group.add_argument(
    "--batch-from-db",
    type=str,
    help="Get all the Work IDs from the database and write them to a simple batch file.",
    metavar="Output File",
)
group.add_argument(
    "--csv-from-db",
    type=str,
    help="Get the contents of the database's 'works' table and write it to a csv file.",
    metavar="Output File",
)
group.add_argument(
    "--polish-batch",
    type=str,
    help="Removes duplicates from target batch file and converts links into work IDs.",
    metavar="File",
)
################################################################
# Doesn't work properly due to bug in upstream ao3_api:
# https://github.com/wendytg/ao3_api/issues/103
################################################################
group.add_argument(
    "--add-series",
    type=str,
    help="Get the IDs of all Works in a specified Series, then output them as a simple batch file.",
    metavar=("Output File", "Series ID/Link"),
    nargs=2,
)
settings.parse()
config = settings.settings

logCore = "io"
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

if settings.args.batch_from_raws:
    setToBatch(
        input=rawsToSet(
            dirRaws=config["dirRaws"],
            logger=logger,
        ),
        output=settings.args.batch_from_raws,
        logger=logger,
    )
elif settings.args.batch_from_db:
    setToBatch(
        input=database.getWorkIdSet(
            filename=config["dbFileFull"],
            logger=logger,
        ),
        output=settings.args.batch_from_db,
        logger=logger,
    )
elif settings.args.csv_from_db:
    dictToCsv(
        input=dbToDict(
            dbFileFull=config["dbFileFull"],
            logger=logger,
        ),
        output=settings.args.csv_from_db,
        logger=logger,
    )
elif settings.args.polish_batch:
    ao3Session = network.login(config=config, logger=logger)
    setToBatch(
        input=batch.parseBatchFile(
            file=settings.args.polish_batch,
            logger=logger,
            ao3Session=ao3Session,
        ),
        output=settings.args.polish_batch,
        logger=logger,
    )
elif settings.args.add_series:
    ao3Session = network.login(config=config, logger=logger)
    setToBatch(
        input=batch.getWorkIdsFromSeriesObj(
            series=network.getSeriesObj(
                seriesID=settings.add_series[1],
                logger=logger,
                ao3Session=ao3Session,
            ),
            logger=logger,
        ),
        output=settings.args.add_series[0],
        logger=logger,
        mode="a",
    )
