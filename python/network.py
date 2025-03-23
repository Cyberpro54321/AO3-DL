#!/usr/bin/env python3

import logging
import random
import time

import AO3

import constants


def getSessionObj(
    username: str,
    password: str,
    logger: logging.Logger,
    retries=constants.loopRetries,
):
    loopNo = 1
    while loopNo < retries:
        try:
            logger.log(
                (10 + (20 * int(loopNo > 9))),
                f"(Attempt {loopNo}): Getting AO3.session object",
            )
            session = AO3.Session(username=username, password=password)
        except (TypeError, AO3.utils.LoginError, AO3.utils.HTTPError) as ex:
            random.seed()
            if type(ex).__name__ == "HTTPError":
                pauseLengthRange = (35, 85)
            else:
                pauseLengthRange = (5, 15)
            pauseLength = random.randrange(pauseLengthRange[0], pauseLengthRange[1])
            logger.warning(
                constants.loopErrorTemplate.format(
                    "getting session object",
                    pauseLength,
                    type(ex).__name__,
                    ex.args,
                )
            )
            time.sleep(pauseLength)
            loopNo += 1
        else:
            loopNo = retries + 10
            return session
    raise Exception(f"Could not get AO3 session object after {retries} attempts.")


def getWorkObjFromId(
    id: int,
    logger: logging.Logger,
    retries: int = constants.loopRetries,
    session=None,
    load=True,
    load_chapters=True,
):
    loopNo = 1
    while loopNo < retries:
        try:
            logger.log(
                (10 + (20 * int(loopNo > 9))),
                f"(Attempt {loopNo}): Getting AO3.work object {id}",
            )
            work = AO3.Work(
                workid=id, session=session, load=load, load_chapters=load_chapters
            )
        except (
            AO3.utils.HTTPError,
            ConnectionError,
            AO3.utils.DownloadError,
            AttributeError,
        ) as ex:
            random.seed()
            pauseLength = random.randrange(35, 85)
            logger.warning(
                constants.loopErrorTemplate.format(
                    f"getting work object for id {id}",
                    pauseLength,
                    type(ex).__name__,
                    ex.args,
                )
            )
            time.sleep(pauseLength)
            loopNo += 1
        else:
            loopNo = retries + 10
            return work
    raise Exception(
        f"Could not get AO3.Work object for work {id} after {retries} attempts"
    )


def downloadWork(
    work: AO3.works.Work,
    filename: str,
    logger: logging.Logger,
    retries: int = constants.loopRetries,
    # useGit: bool = False,
):
    loopNo = 1
    while loopNo < retries:
        try:
            logger.log(
                (10 + (20 * int(loopNo > 9))),
                f"(Attempt {loopNo}): Downloading {work.title}",
            )
            with open(file=filename, mode="wb") as file:
                file.write(work.download("HTML"))
        except AO3.utils.DownloadError as ex:
            random.seed()
            pauseLength = random.randrange(35, 85)
            logger.warning(
                constants.loopErrorTemplate.format(
                    f"downloading work {work.title}",
                    pauseLength,
                    type(ex).__name__,
                    ex.args,
                )
            )
            time.sleep(pauseLength)
            loopNo += 1
        else:
            loopNo = retries + 10
            return True
    raise Exception(
        f"Could not finish downloading {work.title} after {retries} attempts."
    )


# def template(
#     input: str,
#     logger: logging.Logger,
#     retries=constants.loopRetries,
# ):
#     loopNo = 1
#     while loopNo < retries:
#         try:
#             logger.log(
#                 (10 + (20 * int(loopNo > 9))),
#                 f"(Attempt {loopNo}): ACTION",
#             )
#             DO STUFF
#         except Exception as ex:
#             random.seed()
#             pauseLength = random.randrange(35, 85)
#             logger.warning(
#                 constants.loopErrorTemplate.format(
#                     "ERROR MESSAGE",
#                     pauseLength,
#                     type(ex).__name__,
#                     ex.args,
#                 )
#             )
#             time.sleep(pauseLength)
#             loopNo += 1
#         else:
#             loopNo = retries + 10
#             return True
#     raise Exception(
#         f"Could not (GOAL) after {retries} attempts."
#     )
