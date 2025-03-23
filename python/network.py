import logging
import random
import time

import AO3

import constants


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
        else:
            loopNo = retries + 10
            return work
    raise Exception(
        f"Could not get AO3.Work object for work {id} after {loopNo} attempts"
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
        else:
            loopNo = retries + 10
            return True
    raise Exception(
        f"Could not finish downloading {work.title} after {retries} attempts."
    )
