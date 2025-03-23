import logging
import random
import time

import AO3

import constants


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
