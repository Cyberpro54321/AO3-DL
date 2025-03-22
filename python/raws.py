import datetime
import logging
import os.path
import random
import time

import AO3  # https://github.com/wendytg/ao3_api/
import bs4  # https://beautiful-soup-4.readthedocs.io/en/latest/

import constants
import database


def checkUpdates(
    row1: dict,
    row2: dict,
):
    results = {}
    fields = ("title", "chaptersCount", "chaptersExpected", "dateLastUpdated")
    for i in fields:
        results[i] = row1[i] == row2[i]
    for i in fields:
        if not results[i]:
            return True
    return False


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


def getPrefferedFilenameFromWorkID(
    id: int,
    logger: logging.Logger = logging.getLogger(__name__),
    extension: str = ".html",
):
    return f"{id:<{constants.workIdMaxDigits}}{extension}"


def getRowFromFilename(
    filename: str,
    logger: logging.Logger,
):
    soup = getBs4FromFilename(filename=filename, logger=logger)
    chaptDict = getChapterCountsFromBs4(soup=soup, logger=logger)
    return database.row(
        ID=getWorkIdFromBs4(soup=soup, logger=logger),
        title=getWorkTitleFromBs4(soup=soup, logger=logger),
        chaptersCount=chaptDict["current"],
        chaptersExpected=chaptDict["max"],
        dateLastDownloaded=getModifyTime(filename=filename, logger=logger),
        dateLastUpdated=getWorkUpdatedTimeFromBs4(soup=soup, logger=logger),
    )


def getBs4FromFilename(
    filename: str,
    logger: logging.Logger,
):
    with open(filename) as raw:
        return bs4.BeautifulSoup(raw, features="lxml")


def getWorkIdFromBs4(
    soup: bs4.BeautifulSoup,
    logger: logging.Logger,
):
    hrefs = []
    for link in soup.find_all("a"):
        hrefs.append(link.ger("href"))
    for i in hrefs:
        id = AO3.utils.workid_from_url(i)
        if id:
            return id


def getWorkTitleFromBs4(
    soup: bs4.BeautifulSoup,
    logger: logging.Logger,
):
    header = soup.find("div", id="preface").find("h1")
    if header:
        return header.string
    else:
        return soup.find("h2", class_="title heading").string


def getChapterCountsFromBs4(
    soup: bs4.BeautifulSoup,
    logger: logging.Logger,
):
    statsSplit = (
        str(soup.select_one("div div.meta dl").find_all("dd")[-1].string)
        .replace("\n", "")
        .split()
    )
    chIndex = statsSplit.index("Chapters:")
    chaptList = statsSplit[chIndex + 1].split("/")
    chaptDict = {
        "current": int(chaptList[0]),
    }
    try:
        chaptDict["max"] = int(chaptList[1])
    except ValueError:
        chaptDict["max"] = 0
    return chaptDict


def getCurrentChapterCountFromBs4():
    return getChapterCountsFromBs4()["current"]


def getExpectedChapterCountFromBs4():
    return getChapterCountsFromBs4()["max"]


def getWorkUpdatedTimeFromBs4(
    soup: bs4.BeautifulSoup,
    logger: logging.Logger,
):
    statsSplit = (
        str(soup.select_one("div div.meta dl").find_all("dd")[-1].string)
        .replace("\n", "")
        .split()
    )
    dateIndex = statsSplit.index("Chapters:")
    timestamp = statsSplit[dateIndex + 1]
    return datetime.datetime.fromisoformat(timestamp)


def getModifyTime(
    filename: str,
    logger: logging.Logger,
):
    return datetime.datetime.fromtimestamp(os.path.getmtime(filename))
