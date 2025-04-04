#!/usr/bin/env python3

import base64
import logging
import random
import time
import urllib.parse
import urllib.request

import AO3

import constants


def getSeriesObj(
    seriesID: int,
    logger: logging.Logger,
    retries=constants.loopRetries,
) -> AO3.Series:
    loopNo = 1
    while loopNo <= retries:
        try:
            logger.log(
                (10 + (20 * int(loopNo > 9))),
                f"(Attempt {loopNo}): Getting AO3.series object",
            )
            series = AO3.Series(seriesID)
        except Exception as ex:
            random.seed()
            pauseLength = random.randrange(35, 85)
            logger.warning(
                constants.loopErrorTemplate.format(
                    "getting ao3.series object",
                    pauseLength,
                    type(ex).__name__,
                    ex.args,
                )
            )
            time.sleep(pauseLength)
            loopNo += 1
        else:
            loopNo = retries + 10
            return series
    raise Exception(f"Could not get AO3.series object after {retries} attempts.")


def downloadFile(
    url: str,
    dir: str,
    logger: logging.Logger,
    retries: int = 3,
) -> str:
    logger.info(f"Downloading file {url}")
    parseResult = urllib.parse.urlparse(url=url)
    extension = parseResult.path.split("/")[-1].split(".")[-1]
    # above will shit the bed if given a directory URL instead of a file url. Not important for intended usecase
    fileNameCore = base64.urlsafe_b64encode(
        url[int((-252 + len(extension)) * 0.75):].encode()
    ).decode()
    loopNo = 1
    while loopNo <= retries:
        try:
            logger.log(
                (10 + (20 * int(loopNo != 1))),
                f"(Attempt {loopNo}): Downloading file {url}",
            )
            urllib.request.urlretrieve(url, f"{dir}/{fileNameCore}.{extension}")
        except (urllib.error.HTTPError, urllib.error.URLError) as ex:
            random.seed()
            if type(ex).__name__ == "HTTPError":
                pauseLengthRange = (35, 85)
            else:
                pauseLengthRange = (5, 15)
            pauseLength = random.randrange(pauseLengthRange[0], pauseLengthRange[1])
            logger.warning(
                constants.loopErrorTemplate.format(
                    f"downloading file {url}",
                    pauseLength,
                    type(ex).__name__,
                    ex.args,
                )
            )
            time.sleep(pauseLength)
            loopNo += 1
        else:
            loopNo = retries + 10
            logger.info(
                f"Successfully downloaded file {url} as\n{fileNameCore}.{extension}"
            )
            return f"{fileNameCore}.{extension}"
    return url


def getSessionObj(
    username: str,
    password: str,
    logger: logging.Logger,
    retries=constants.loopRetries,
):
    logger.info("Logging in...")
    loopNo = 1
    while loopNo <= retries:
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
    while loopNo <= retries:
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
    useGit: bool = False,
):
    loopNo = 1
    while loopNo <= retries:
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
            if useGit:
                import subprocess
                import os.path

                dirRaws = os.path.dirname(filename)
                subprocess.run(
                    ["git", "-C", dirRaws, "add", os.path.basename(filename)]
                )
                subprocess.run(
                    [
                        "git",
                        "-C",
                        dirRaws,
                        "commit",
                        "-m",
                        f"New raw downloaded for {work.id}",
                    ]
                )
                subprocess.run(["git", "-C", dirRaws, "push"])
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
#     while loopNo <= retries:
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
