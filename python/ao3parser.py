#!/usr/bin/env python3
import concurrent.futures
import json

import AO3
import bs4

import constants
import download
import init


def getSeriesObj(
    seriesID: int,
    logger: init.logging.Logger,
    retries: int = constants.loopRetries,
    ao3Session: AO3.Session = None,
    tryAnon: bool = True,
) -> AO3.Series:
    loopNo = 1
    if tryAnon:
        ao3SessionInUse = None
    else:
        ao3SessionInUse = ao3Session
    while loopNo <= retries:
        try:
            logger.log(
                (10 + (20 * int(loopNo > 9))),
                f"Attempt [{loopNo}] getting AO3.Series object [{workID}]",
            )
            series = AO3.Series(seriesid=seriesID, session=ao3SessionInUse)
        except (AttributeError,) as ex:
            download.loopWait(
                loopNo=loopNo,
                ex=ex,
                goal="AO3.Series",
                id=str(seriesID),
                errLevel=init.logging.INFO,
                logger=logger,
            )
        else:
            logger.info(f"Got AO3.Series object [{seriesID}]")
            loopNo = retries * 10
            return series


def getAuthorObj(
    username: str,
    logger: init.logging.Logger,
    retries: int = constants.loopRetries,
    ao3Session: AO3.Session = None,
    tryAnon: bool = True,
) -> AO3.User:
    loopNo = 1
    if tryAnon:
        ao3SessionInUse = None
    else:
        ao3SessionInUse = ao3Session
    while loopNo <= retries:
        try:
            logger.log(
                (10 + (20 * int(loopNo > 9))),
                f"Attempt [{loopNo}] getting AO3.User object [{username}]",
            )
            author = AO3.User(username=username, session=ao3SessionInUse)
        except (AttributeError,) as ex:
            download.loopWait(
                loopNo=loopNo,
                ex=ex,
                goal="AO3.User",
                id=str(username),
                errLevel=init.logging.INFO,
                logger=logger,
            )
        else:
            logger.info(f"Got AO3.User object [{username}]")
            loopNo = retries * 10
            return author


init.init(json="r")
logger = init.logger
config = init.config

workIDs = set(())
seriesIDs = set(())
authors = set(())

inRaw = init.parseInfile(init.args.infile, init.errLogger)
for line in inRaw:
    if line.isdecimal():
        init.logger.warning(
            f"Plain int [{line}] passed to parser.py, assuming it is a workID."
        )
        workIDs.add(int(line))
    elif line[1:].isdecimal():
        match line[:1].lower():
            case "w":
                workID = int(line[1:])
                init.logger.debug(f"Parsed [{line}] into workID [{workID}]")
                workIDs.add(workID)
            case "s":
                seriesID = int(line[1:])
                init.logger.debug(f"Parsed [{line}] into series ID [{seriesIDs}]")
                seriesIDs.add(seriesID)
    elif line[:4] == "http" or -1 < line.find("archiveofourown.org") <= 12:
        split = line.split("/")
        match split[3]:
            case "works":
                workID = int(split[4])
                logger.debug(f"Parsed [{line}] into workID [{workID}]")
                workIDs.add(workID)
            case "series":
                seriesID = int(split[4])
                logger.debug(f"Parsed [{line}] into seriesID [{seriesID}]")
                seriesIDs.add(seriesID)
            case "users":
                author = str(split[4])
                logger.debug(f"Parsed [{line}] into author [{author}]")
                authors.add(author)
    else:
        authors.add(line)
        init.logger.warning(
            f"Plain string [{line}] passed to parser.py, assuming it is an author username."
        )

for workID in workIDs:
    logger.info(f"WorkID [{workID}]")
for seriesID in seriesIDs:
    logger.info(f"SeriesID [{seriesID}]")
for author in authors:
    logger.info(f"Author [{author}]")

futuresSeries = {}
futuresAuthors = {}

with concurrent.futures.ThreadPoolExecutor(
    max_workers=10, thread_name_prefix=constants.threadNameBulk
) as pool1:
    for seriesID in seriesIDs:
        futuresSeries[seriesID] = pool1.submit(getSeriesObj, seriesID, logger)
    for author in authors:
        futuresAuthors[author] = pool1.submit(getAuthorObj, author, logger)

seriesObjs = []
authorObjs = []
for series in futuresSeries:
    try:
        result = futuresSeries[series].result()
    except (Exception,) as ex:
        init.errLogger.error(
            f"Series [{series}] raised [{type(ex).__name__}]: [{ex.args}]"
        )
    else:
        seriesObjs.append(result)
for author in futuresAuthors:
    try:
        result = futuresAuthors[author].result()
    except (Exception,) as ex:
        init.errLogger.error(
            f"Author [{author}] raised [{type(ex).__name__}]: [{ex.args}]"
        )
    else:
        authorObjs.append(result)

for seriesObj in seriesObjs:
    if len(seriesObj.work_list) != seriesObj.nworks:
        errStr = f"Series [{seriesObj.id} - {seriesObj.name}] claims to have [{seriesObj.nworks}] works, but Series.work_list returned only [{len(seriesObj.work_list)}] works."
        init.errLogger.critical(errStr)
        raise Exception(errStr)
for authorObj in authorObjs:
    works = author.get_works()
    if len(works) != author.works:
        errStr = f"Author [{author.username}] claims to have [{author.works}] works, but User.get_works() returned only [{len(works)}] works."
        init.errLogger.critical(errStr)
        raise Exception(errStr)
    for work in works:
        workIDs.add(work.id)


futuresWorks = {}
workObjs = []
with concurrent.futures.ThreadPoolExecutor(
    max_workers=10, thread_name_prefix=constants.threadNameBulk
) as pool2:
    for workID in workIDs:
        futuresWorks[workID] = pool2.submit(download.getWorkObj, workID, logger)
