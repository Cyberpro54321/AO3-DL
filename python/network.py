#!/usr/bin/env python3

import base64
import logging
import os.path
import random
import time
import urllib.parse
import urllib.request

import AO3

import constants

import requests.exceptions


def getSeriesObj(
    seriesID: str,
    logger: logging.Logger,
    retries: int = constants.loopRetries,
    ao3Session: AO3.Session = None,
) -> AO3.Series:
    loopNo = 1
    while loopNo <= retries:
        try:
            logger.log(
                (10 + (20 * int(loopNo > 9))),
                f"(Attempt {loopNo}): Getting AO3.Series object {seriesID}",
            )
            series = AO3.Series(seriesID, session=ao3Session)
            series.nworks
        except (ConnectionError, AttributeError) as ex:
            random.seed()
            pauseLength = random.randrange(5, 15)
            logger.warning(
                constants.loopErrorTemplate.format(
                    f"getting ao3.Series object {seriesID}",
                    pauseLength,
                    type(ex).__name__,
                    ex.args,
                )
            )
            time.sleep(pauseLength)
            loopNo += 1
        else:
            logger.info(f"Got AO3.Series object {seriesID}")
            loopNo = retries + 10
            return series
    raise Exception(
        f"Could not get AO3.Series object {seriesID} after {retries} attempts."
    )


def downloadFile(
    url: str,
    dir: str,
    logger: logging.Logger,
    retries: int = 3,
) -> str:
    parseResult = urllib.parse.urlparse(url=url)
    extension = parseResult.path.split("/")[-1].split(".")[-1]
    # above will shit the bed if given a directory URL instead of a file url. Not important for intended usecase
    fileNameCore = base64.urlsafe_b64encode(
        url[int((-252 + len(extension)) * 0.75):].encode()
    ).decode()
    fileName = f"{fileNameCore}.{extension}"
    if os.path.exists(fileName) and os.path.getsize(fileName):
        return fileName
    logger.info(f"Downloading file {url}")
    loopNo = 1
    while loopNo <= retries:
        try:
            logger.log(
                (10 + (20 * int(loopNo != 1))),
                f"(Attempt {loopNo}): Downloading file {url}",
            )
            urllib.request.urlretrieve(url, f"{dir}/{fileName}")
        except (urllib.error.HTTPError, urllib.error.URLError) as ex:
            random.seed()
            badHost = ""
            for i in (
                ("cdn.discordapp.com", "Discord CDN"),
                ("media.discordapp.net", "Discord CDN"),
                ("i.imgur.com", "Imgur"),
                ("imgur.com", "Imgur"),
            ):
                if (
                    type(ex).__name__ == "HTTPError"
                    and parseResult.netloc[: len(i[0])].lower() == i[0].lower()
                ):
                    badHost = i[1]
            if badHost:
                logger.error(f"{badHost} Image Hosting Detected")
                loopNo += 100
                continue
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
            return fileName
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


def login(
    config: dict,
    logger: logging.Logger,
) -> AO3.Session:
    if config["ao3DoLogin"]:
        with open(config["ao3UsernameFile"]) as file:
            ao3Username = file.readline().strip()
        with open(config["ao3PasswordFile"]) as file:
            ao3Password = file.readline().strip()
        session = getSessionObj(
            username=ao3Username, password=ao3Password, logger=logger
        )
        del ao3Username
        del ao3Password
    else:
        session = None
    return session


def getWorkObjFromId(
    id: int,
    logger: logging.Logger,
    retries: int = constants.loopRetries,
    session=None,
    load=True,
    load_chapters=True,
):
    loopNo = 1
    errors = {}
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
            requests.exceptions.ConnectionError,
        ) as ex:
            errors[loopNo] = type(ex).__name__
            if loopNo > 10:
                attErrs = 0
                for i in errors:
                    if errors[i] == "AttributeError":
                        attErrs += 1
                if attErrs > (0.9 * loopNo):
                    logger.error(f"Work ID {id} seems to be unavailable")
                    return False
            random.seed()
            if type(ex).__name__ == "AttributeError":
                pauseLength = random.randrange(5, 15)
            else:
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
        except (
            AO3.utils.DownloadError,
            AO3.utils.HTTPError,
            ConnectionError,
            requests.exceptions.ConnectionError,
        ) as ex:
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
