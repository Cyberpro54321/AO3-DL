import os.path
import pickle
import random
import time

import AO3

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
        except (AttributeError,) as ex:
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
