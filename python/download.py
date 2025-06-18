#!/usr/bin/env python3
import concurrent.futures
import datetime
import os.path
import pickle
import random
import time
import traceback

import AO3
import bs4

import constants
import init


def loopWait(
    loopNo: int,
    ex: Exception,
    goal: str,
    errLevel: int,
    logger: init.logging.Logger,
    id: str = "",
) -> None:
    random.seed()
    pauseMult = 0.5 + random.random()
    pauseTime = int(loopNo * 5 * pauseMult)
    if id:
        string = f"getting {goal} obj for [{id}]"
    else:
        string = f"getting {goal} obj"
    logger.log(
        errLevel,
        constants.loopErrorTemplate.format(
            string,
            pauseTime,
            type(ex).__name__,
            ex.args,
        ),
    )
    time.sleep(pauseTime)


def getWorkObj(
    workID: int,
    logger: init.logging.Logger,
    errLogger: init.logging.Logger = None,
    retries: int = constants.loopRetries,
    ao3Session: AO3.Session = None,
    tryAnon: bool = True,
) -> AO3.Work:
    if not errLogger:
        errLogger = logger
    loopNo = 1
    if tryAnon:
        ao3SessionInUse = None
    else:
        ao3SessionInUse = ao3Session
    while loopNo <= retries:
        try:
            logger.log(
                (10 + (20 * int(loopNo > 9))),
                f"Attempt [{loopNo}] getting AO3.Work object [{workID}]",
            )
            work = AO3.Work(
                workid=workID,
                session=ao3SessionInUse,
                load=True,
                load_chapters=False,
            )
        except AO3.utils.PrivateWorkError:
            if ao3SessionInUse:
                errStr = f"Work [{workID}] threw PrivateWorkError despite valid ao3SessionInUse???"
                errLogger.critical(errStr)
                raise Exception(errStr)
            else:
                if ao3Session:
                    ao3SessionInUse = ao3Session
                    logStr = f"Work [{workID}] requires login, will now use provided AO3.Session."
                    logger.info(logStr)
                else:
                    errStr = f"Work [{workID}] requires login but no AO3.Session was provided."
                    errLogger.critical(errStr)
                    raise Exception(errStr)
        except (AO3.utils.HTTPError,) as ex:
            loopWait(
                loopNo=loopNo,
                ex=ex,
                goal="AO3.Work",
                id=str(workID),
                errLevel=init.logging.INFO,
                logger=logger,
            )
            loopNo += 1
        else:
            logger.info(f"Got AO3.Work object [{workID}]")
            loopNo = retries * 10
            return work


def getSessionObj(
    usernameFilepath: str,
    passwordFilepath: str,
    logger: init.logging.Logger,
    errLogger: init.logging.Logger = None,
    pickleFilepath: str = "",
    retries: int = constants.loopRetries,
) -> AO3.Session:
    if not errLogger:
        errLogger = logger
    if (
        pickleFilepath
        and os.path.exists(pickleFilepath)
        and os.path.getsize(pickleFilepath)
    ):
        with open(pickleFilepath, "rb") as file:
            session = pickle.load(file)
        return session
    usernameExists = bool(
        os.path.exists(usernameFilepath) and os.path.getsize(usernameFilepath)
    )
    passwordExists = bool(
        os.path.exists(passwordFilepath) and os.path.getsize(passwordFilepath)
    )
    if (not usernameExists) and (not passwordExists):
        errStr = f"Username & password files [{usernameFilepath}] and [{passwordFilepath}] either don't exist or are 0 bytes long."
        errLogger.critical(errStr)
        raise Exception(errStr)
    if not usernameExists:
        errStr = f"Username file [{usernameFilepath}] either doesn't exist or is 0 bytes long."
        errLogger.critical(errStr)
        raise Exception(errStr)
    if not passwordExists:
        errStr = f"Password file [{passwordFilepath}] either doesn't exist or is 0 bytes long."
        errLogger.critical(errStr)
        raise Exception(errStr)
    loopNo = 1
    with open(usernameFilepath) as file:
        usernameStr = file.read().strip()
    with open(passwordFilepath) as file:
        passwordStr = file.read().strip()
    while loopNo <= retries:
        try:
            logger.log(
                (10 + (20 * int(loopNo > 9))),
                f"Attempt [{loopNo}] getting AO3.Session object.",
            )
            session = AO3.Session(usernameStr, passwordStr)
        except (AO3.utils.HTTPError,) as ex:
            loopWait(
                loopNo=loopNo,
                ex=ex,
                goal="AO3.Session",
                errLevel=init.logging.INFO,
                logger=logger,
            )
            loopNo += 1
        else:
            logger.info("Got AO3.Session object")
            loopNo = retries * 10
    if pickleFilepath:
        os.makedirs(os.path.dirname(pickleFilepath), exist_ok=True)
        with open(pickleFilepath, "wb") as file:
            pickle.dump(session, file)
    return session


def login(
    config: dict,
    logger: init.logging.Logger,
    errLogger: init.logging.Logger = None,
) -> AO3.Session | None:
    if not errLogger:
        errLogger = logger
    if config["ao3DoLogin"]:
        session = getSessionObj(
            usernameFilepath=config["ao3UsernameFile"],
            passwordFilepath=config["ao3PasswordFile"],
            logger=logger,
            errLogger=errLogger,
            pickleFilepath=config["ao3SessionPickle"],
        )
    else:
        session = None
    return session


def getWorkskin(
    work: AO3.Work,
    logger: init.logging.Logger,
    version: str = constants.version,
) -> str:
    workskin = ""
    try:
        workskin = work.workskin
    except AttributeError:
        allStyles = work._soup.find_all("style", {"type": "text/css"})
        if len(allStyles) != 0:
            text = str(allStyles[-1].decode_contents())
            if text.find("#workskin") != -1:
                workskin = text
    if workskin:
        logger.info(
            f"Got [{len(workskin)}] characters of workskin from work [{work.id}]"
        )
        workskin += f"/*AO3-DL Version: {version}*/"
        workskin += f"/*AO3-DL Date Saved: {datetime.date.today().isoformat()}*/"
    else:
        logger.info(f"Could not find a workskin in work [{work.id}]")
    return workskin


def processNode(
    work: AO3.Work,
) -> bool:
    return True


if __name__ == "__main__":
    ################################################################
    # Stage 1: Initialization
    ################################################################
    init.init(json="r")
    workIDs = set(())
    inRaw = init.parseInfile(init.args.infile, init.errLogger)
    for line in inRaw:
        try:
            workIDs.add(int(line))
        except ValueError:
            init.errLogger.error(f"Could not convert input [{line}] to int")
    init.logger.info(f"Got [{len(workIDs)}] workIDs")
    ################################################################
    # Stage 2: Get All Work Objects
    ################################################################
    session = login(
        config=init.config,
        logger=init.logger,
        errLogger=init.errLogger,
    )
    futures = {}
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=10, thread_name_prefix=constants.threadNameBulk
    ) as pool1:
        for workID in workIDs:
            futures[workID] = pool1.submit(
                getWorkObj,
                workID=workID,
                logger=init.logger,
                errLogger=init.errLogger,
                ao3Session=session,
                tryAnon=(not init.config["ao3DoLoginAlways"]),
            )
    workObjs = {}
    for workID in futures:
        try:
            result = futures[workID].result()
        except Exception as ex:
            init.errLogger.error(
                f"Work [{workID}] raised [{type(ex).__name__}] while getting AO3.Work object: [{ex.args}]"
            )
            traceback.print_exception(ex)
        else:
            workObjs[workID] = result
    del futures
    init.logger(f"Got [{len(workObjs)}] AO3.Work objects before blacklist filtering")
    ################################################################
    # Stage 3: Blacklist / Whitelist Filtering
    ################################################################

    workObjsFiltered = {}
    for workID in workObjs:
        if processNode(workObjs[workID]):
            init.logger.info(f"Work [{workID}] passed the blacklist")
            workObjsFiltered[workID] = workObjs[workID]
        else:
            init.logger.info(f"Work [{workID}] failed the blacklist")
    del workObjs
    init.logger(
        f"Got [{len(workObjsFiltered)}] AO3.Work objects after blacklist filtering"
    )

    ################################################################
    # Stage 4: Save .css and .html files
    ################################################################
    workskinsFound = 0
    for work in workObjsFiltered:
        workskin = getWorkskin(work=work, logger=init.logger)
        if workskin:
            workskinsFound += 1
            with open(
                os.path.join(init.config["dirRaws"], f"{work.id:0>8}.css"), "w"
            ) as file:
                file.write(workskin)
    init.logger(f"Wrote [{workskinsFound}] workskin files")
    del workskinsFound
    futures2 = {}
    raws = {}
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=10, thread_name_prefix=constants.threadNameBulk
    ) as pool2:
        for work in workObjsFiltered:
            futures2[work.id] = pool2.submit(work.download, filetype="HTML")
    for workID in futures2:
        try:
            result = futures2[workID].result()
        except Exception as ex:
            init.errLogger.error(
                f"Work [{workID}] raised [{type(ex).__name__}] while downloading raw: [{ex.args}]"
            )
            traceback.print_exception(ex)
        else:
            raws[workID] = result
    for workID in raws:
        soup = bs4.BeautifulSoup(raws[workID], "lxml")
        soup.append(bs4.Comment(f"{constants.commentVersion}{constants.version}"))
        soup.append(
            bs4.Comment(
                f"{constants.commentTimestampEdited}{workObjsFiltered[workID].date_edited.isoformat()}"
            )
        )
        soup.append(
            bs4.Comment(
                f"{constants.commentTimestampDownloaded}{datetime.datetime.now().isoformat()}"
            )
        )
        with open(
            os.path.join(init.config["dirOut"], f"{workID:0>8}.html"), "w"
        ) as file:
            file.write(soup.prettify(formatter="html5"))
