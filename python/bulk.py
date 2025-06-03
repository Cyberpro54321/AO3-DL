#!/usr/bin/env python3

import concurrent.futures
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
    setErrImg = main.main(work=work, config=config, logger=logger)
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
settings.parser.add_argument(
    "input",
    type=str,
    help="If present, download and format all works in the specified batch file. Otherwise re-downloads all works in database",
    metavar="BATCH",
    nargs="?",
    default="",
)
settings.parse()
config = settings.settings


logger = getLogger.getLogger(
    level=config["logsLevel"],
    includeThreadName=True,
)

session = network.login(config=config, logger=logger)


if not os.path.exists(config["dbFileFull"]):
    database.initDB(filename=config["dbFileFull"], logger=logger)

ids = set(())
completed = set(())
if settings.args.input:
    for id in batch.parseBatchFile(
        file=os.path.expanduser(settings.args.input),
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

errLogger = getLogger.getLogger(
    level=config["logsLevel"],
    mode="stderr",
)
for i in ids.difference(completed):
    errLogger.error("Work {" + i + "} failed to complete")
for i in incompleteImg:
    errLogger.error("Image {" + i + "} couldn't be downloaded")


logger.info("Mostly complete, checking for exceptions from threads")

for i in futures:
    try:
        futures[i].result()
    except AO3.utils.InvalidIdError:
        logger.error(f"WorkID {i} not found (Error 404)")

logger.info("Complete, bulk.py exiting")
