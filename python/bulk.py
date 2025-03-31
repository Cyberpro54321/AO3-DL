#!/usr/bin/env python3

import concurrent.futures
import datetime
import os.path

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
    logger.info(f"Got AO3.Work object for {id}")
    main.main(work=work, config=config, logger=logger, forceDownloadNew=download_all)
    global completed
    completed.add(id)
    global worksComplete
    global worksTotal
    worksComplete += 1
    logger.info(f"Completed {id} - Work {worksComplete}/{worksTotal}")


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

if config["ao3DoLogin"]:
    with open(config["ao3UsernameFile"]) as file:
        ao3Username = file.readline().strip()
    with open(config["ao3PasswordFile"]) as file:
        ao3Password = file.readline().strip()
    session = network.getSessionObj(
        username=ao3Username, password=ao3Password, logger=logger
    )
    del ao3Username
    del ao3Password
else:
    session = None


if not os.path.exists(config["dbFileFull"]):
    database.initDB(filename=config["dbFileFull"], logger=logger)

ids = set(())
completed = set(())
if from_batch:
    batchBuffer = []
    with open(os.path.expanduser(from_batch)) as batchfile:
        for i in batchfile:
            batchBuffer.append(i.strip())
    for i in batchBuffer:
        ids.add(main.parseInput(input=str(i), logger=logger))
else:
    ids = database.getWorkIdSet(filename=config["dbFileFull"], logger=logger)

worksComplete = 0
worksTotal = len(ids)

with concurrent.futures.ThreadPoolExecutor(
    max_workers=10, thread_name_prefix="worker"
) as pool:
    for i in ids:
        pool.submit(primary, i)

for i in ids.difference(completed):
    errorMsg = f"Work {i} failed to complete"
    print(errorMsg)
    logger.error(errorMsg)


logger.info("Complete, bulk.py exiting")
