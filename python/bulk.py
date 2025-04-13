#!/usr/bin/env python3

import concurrent.futures
import datetime
import os.path

import AO3

import batch
import constants
import database
import getLogger
import main
import network
import settings


def primary(id):
    logger.info(f"Starting {id}")
    work = network.getWorkObjFromId(
        id=id,
        logger=logger,
        session=session,
        load_chapters=False,
    )
    if work is False:
        return False
    logger.info(f"Got AO3.Work object for {id}")
    setErrImg = main.main(
        work=work, config=config, logger=logger, forceDownloadNew=download_all
    )
    global incompleteImg
    for i in setErrImg:
        incompleteImg.add(i)
    global completed
    completed.add(id)
    global worksComplete
    global worksTotal
    worksComplete += 1
    logger.info(f"Completed {id} - Work {worksComplete}/{worksTotal}")
    return True


settings.setup()
groupAction = settings.parser.add_mutually_exclusive_group(required=True)
groupAction.add_argument(
    "--download-updates",
    action="store_true",
    help="Go through all works in the database, then re-download and re-format any with updates since the version on file.",
)
groupAction.add_argument(
    "--download-all",
    action="store_true",
    help="Re-download and re-format all works in database, even if no updates.",
)
groupAction.add_argument(
    "--from-batch",
    type=str,
    help="Download and format all works in a specified batch file, without re-downloading any up-to-date Raws already present.",
    metavar="FILE",
)
settings.parse()
config = settings.settings
download_updates = settings.args.download_updates
download_all = settings.args.download_all
from_batch = settings.args.from_batch


logCore = "bulk"
if config["logsTimestamp"]:
    logAppend = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
else:
    logAppend = "latest"
logger = getLogger.getLogger(
    core=logCore,
    append=logAppend,
    dirLogs=config["dirLogs"],
    level=config["logsLevel"],
    includeThreadName=True,
)

session = network.login(config=config, logger=logger)


if not os.path.exists(config["dbFileFull"]):
    database.initDB(filename=config["dbFileFull"], logger=logger)

ids = set(())
completed = set(())
if from_batch:
    for id in batch.parseBatchFile(
        file=os.path.expanduser(from_batch),
        logger=logger,
    ):
        ids.add(id)
else:
    ids = database.getWorkIdSet(filename=config["dbFileFull"], logger=logger)

worksComplete = 0
worksTotal = len(ids)
incompleteImg = set(())

futures = {}
with concurrent.futures.ThreadPoolExecutor(
    max_workers=10, thread_name_prefix=constants.threadNameBulk
) as pool:
    for i in ids:
        futures[i] = pool.submit(primary, i)

if config["useGit"]:
    main.acp(dirRaws=config["dirRaws"], logger=logger)

with open(f'{config["dirLogs"]}/err-bulk-workIncomplete.txt', "w") as errorFile:
    for i in ids.difference(completed):
        errorMsg = f"Work {i} failed to complete"
        print(errorMsg)
        logger.error(errorMsg)
        errorFile.write(f"{i}\n")


with open(f"{config['dirLogs']}/err-bulk-imgIncomplete.log", "w") as fileErrImg:
    for i in incompleteImg:
        fileErrImg.write(f"{i}\n")


logger.info("Mostly complete, checking for exceptions from threads")

for i in futures:
    try:
        futures[i].result()
    except AO3.utils.InvalidIdError:
        errStr = f"WorkID {i} not found (Error 404)"
        print(errStr)
        logger.error(errStr)
        del errStr

logger.info("Complete, bulk.py exiting")
