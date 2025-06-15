import logging
import pickle
import random
import time

import AO3

import constants


def loopWait(
    loopNo: int,
    ex: Exception,
    goal: str,
    id: str,
    errLevel: int,
    logger: logging.Logger,
) -> None:
    random.seed()
    pauseMult = 0.5 + random.random()
    pauseTime = int(loopNo * 5 * pauseMult)
    logger.log(
        errLevel,
        constants.loopErrorTemplate.format(
            f"getting {goal} obj for [{id}]",
            pauseTime,
            type(ex).__name__,
            ex.args,
        ),
    )
    time.sleep(pauseTime)


def getWorkObj(
    workID: int,
    logger: logging.Logger,
    retries: int = constants.loopRetries,
    ao3Session: AO3.Session = None,
    tryAnon: bool = True,
) -> AO3.Work:
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
        except (AttributeError,) as ex:
            loopWait(
                loopNo=loopNo,
                ex=ex,
                goal="AO3.Work",
                id=str(workID),
                errLevel=logging.INFO,
                logger=logger,
            )
        else:
            logger.info(f"Got AO3.Work object [{workID}]")
            loopNo = retries * 10
            return work


def getSessionObj():
    pass
