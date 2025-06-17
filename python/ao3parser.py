#!/usr/bin/env python3
import concurrent.futures
import json
import traceback

import AO3
import bs4

import constants
import download
import init


def getSeriesObj(
    seriesID,
    logger: init.logging.Logger,
    errLogger: init.logging.Logger,
    retries: int,
    ao3Session: AO3.Session,
    tryAnon: bool,
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
                f"Attempt [{loopNo}] getting AO3.Series object [{seriesID}]",
            )
            series = AO3.Series(seriesid=seriesID, session=ao3SessionInUse)
        except AO3.utils.PrivateWorkError:
            if ao3SessionInUse:
                errStr = f"Series [{seriesID}] threw PrivateWorkError despite valid ao3SessionInUse???"
                errLogger.critical(errStr)
                raise Exception(errStr)
            else:
                if ao3Session:
                    ao3SessionInUse = ao3Session
                    logStr = f"Series [{seriesID}] requires login, will now use provided AO3.Session."
                    logger.info(logStr)
                else:
                    errStr = f"Series [{seriesID}] requires login but no AO3.Session was provided."
                    errLogger.critical(errStr)
                    raise Exception(errStr)
        except (AO3.utils.HTTPError,) as ex:
            download.loopWait(
                loopNo=loopNo,
                ex=ex,
                goal="AO3.Series",
                id=str(seriesID),
                errLevel=init.logging.INFO,
                logger=logger,
            )
            loopNo += 1
        else:
            logger.info(f"Got AO3.Series object [{seriesID}]")
            loopNo = retries * 10
            return series


def getSeriesWorks(
    seriesID: int,
    logger: init.logging.Logger,
    errLogger: init.logging.Logger = None,
    retries: int = constants.loopRetries,
    session: AO3.Session = None,
    tryAnon: bool = True,
) -> set:
    if not errLogger:
        errLogger = logger
    series = getSeriesObj(
        seriesID=seriesID,
        logger=logger,
        errLogger=errLogger,
        retries=retries,
        ao3Session=session,
        tryAnon=tryAnon,
    )
    outWorks = []
    outWorks.extend(series.work_list)
    pagesCount = 1
    if series.nworks != len(series.work_list):
        pagesSet = divmod(series.nworks, constants.ao3WorksPerSeriesPage)
        pagesCount = pagesSet[0] + int(bool(pagesSet[1]))
        for i in range(2, 1 + pagesCount):
            page = getSeriesObj(
                seriesID=f"{seriesID}?page={i}",
                logger=logger,
                errLogger=errLogger,
                retries=retries,
                ao3Session=session,
                tryAnon=tryAnon,
            )
            outWorks.extend(page.work_list)
    if series.nworks != len(outWorks):
        errLogger.error(
            f"Series [{seriesID}] nworks [{series.nworks}] != len(work_list) [{len(outWorks)}] after loading [{pagesCount -1}] more pages."
        )
        errLogger.error(f"[{seriesID}]: [{outWorks}]")
    outSet = set(())
    for work in outWorks:
        outSet.add(work.id)
    return outSet


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
        except (AO3.utils.HTTPError,) as ex:
            download.loopWait(
                loopNo=loopNo,
                ex=ex,
                goal="AO3.User",
                id=str(username),
                errLevel=init.logging.INFO,
                logger=logger,
            )
            loopNo += 1
        else:
            logger.info(f"Got AO3.User object [{username}]")
            loopNo = retries * 10
            return author


def getAuthorWorks(
    username: str,
    logger: init.logging.Logger,
    errLogger: init.logging.Logger = None,
    retries: int = constants.loopRetries,
) -> set:
    if not errLogger:
        errLogger = logger
    author = getAuthorObj(username=username, logger=logger, retries=retries)
    loopNo = 1
    while loopNo <= retries:
        try:
            works = author.get_works()
        except AO3.utils.HTTPError as ex:
            download.loopWait(
                loopNo=loopNo,
                ex=ex,
                goal="AO3.User.get_works()",
                id=str(username),
                errLevel=init.logging.INFO,
                logger=logger,
            )
            loopNo += 1
        else:
            loopNo = retries * 10
    if len(works) != author.works:
        errStr = f"Author [{author.username}] claims to have [{author.works}] works, but User.get_works() returned only [{len(works)}] works."
        errLogger.critical(errStr)
        raise Exception(errStr)
    outSet = set(())
    for work in works:
        outSet.add(work.id)
    return outSet


init.init(json="r")
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
                init.logger.debug(f"Parsed [{line}] into workID [{workID}]")
                workIDs.add(workID)
            case "series":
                seriesID = int(split[4])
                init.logger.debug(f"Parsed [{line}] into seriesID [{seriesID}]")
                seriesIDs.add(seriesID)
            case "users":
                author = str(split[4])
                init.logger.debug(f"Parsed [{line}] into author [{author}]")
                authors.add(author)
    else:
        authors.add(line)
        init.logger.warning(
            f"Plain string [{line}] passed to parser.py, assuming it is an author username."
        )

for workID in workIDs:
    init.logger.info(f"WorkID [{workID}]")
for seriesID in seriesIDs:
    init.logger.info(f"SeriesID [{seriesID}]")
for author in authors:
    init.logger.info(f"Author [{author}]")

futuresSeries = {}
futuresAuthors = {}

if config["ao3DoLogin"]:
    session = download.getSessionObj(
        usernameFilepath=config["ao3UsernameFile"],
        passwordFilepath=config["ao3PasswordFile"],
        logger=init.logger,
        errLogger=init.errLogger,
        pickleFilepath=config["ao3SessionPickle"],
    )
else:
    session = None

with concurrent.futures.ThreadPoolExecutor(
    max_workers=10, thread_name_prefix=constants.threadNameBulk
) as pool1:
    for seriesID in seriesIDs:
        futuresSeries[seriesID] = pool1.submit(
            getSeriesWorks,
            seriesID,
            init.logger,
            init.errLogger,
            session=session,
            tryAnon=(not config["ao3DoLoginAlways"]),
        )
    for author in authors:
        futuresAuthors[author] = pool1.submit(
            getAuthorWorks, author, init.logger, init.errLogger
        )

init.logger.info("Retreiving from futures...")

seriesContents = []
authorContents = []
for series in futuresSeries:
    try:
        result = futuresSeries[series].result()
    except (Exception,) as ex:
        init.errLogger.error(
            f"Series [{series}] raised [{type(ex).__name__}]: [{ex.args}]"
        )
        traceback.print_exception(ex)
    else:
        seriesContents.append(result)
for author in futuresAuthors:
    try:
        result = futuresAuthors[author].result()
    except (Exception,) as ex:
        init.errLogger.error(
            f"Author [{author}] raised [{type(ex).__name__}]: [{ex.args}]"
        )
        traceback.print_exception(ex)
    else:
        authorContents.append(result)

for series in seriesContents:
    for workID in series:
        workIDs.add(workID)
for author in authorContents:
    for workID in author:
        workIDs.add(workID)

for workID in workIDs:
    init.logger.info(f"WorkID [{workID}]")

# futuresWorks = {}
# workObjs = []
# with concurrent.futures.ThreadPoolExecutor(
#     max_workers=10, thread_name_prefix=constants.threadNameBulk
# ) as pool2:
#     for workID in workIDs:
#         futuresWorks[workID] = pool2.submit(download.getWorkObj, workID, logger)
