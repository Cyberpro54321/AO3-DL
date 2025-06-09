#!/usr/bin/env python3
# import concurrent.futures
import datetime
import logging
import os.path
import platform

import bs4

import constants
import db
import init


def tagToFile(
    tag,
    filename: str,
) -> None:
    if isinstance(tag, str):
        tagStr = tag
    if isinstance(tag, list):
        tagStr = ""
        for i in tag:
            tagStr += i.prettify(formatter="html5")
    if isinstance(tag, bs4.Tag):
        tagStr = tag.prettify(formatter="html5")
    with open(filename, "w") as file:
        file.write(tagStr)


def processSingle(
    workID: int,
    config: dict,
    logger: logging.Logger,
) -> None:
    logger.info(f"Processing [{workID}]")
    sqlInfo = {}
    rawFilename = os.path.join(
        config["dirRaws"], f"{workID:0>{constants.workIdMaxDigits}}.html"
    )
    with open(rawFilename) as rawFile:
        rawSoup = bs4.BeautifulSoup(rawFile, features="lxml")
    wIdFolder = os.path.join(config["dirOut"], f"{workID:0>8}")
    if not os.path.exists(wIdFolder):
        os.mkdir(wIdFolder)
    if not os.path.isdir(wIdFolder):
        raise Exception

    ################################################################
    # Tag Isolation
    ################################################################
    ################################
    # TagsDiv
    ################################
    headerMeta = rawSoup.find(id="preface").div
    tagsDiv = headerMeta.dl
    tagsDiv["class"] = ["works meta group"]
    workTags = tagsDiv.find_all("dd")
    workTagHeadersRaw = tagsDiv.find_all("dt")
    workTagHeaders = []
    for tag in workTagHeadersRaw:
        tagStr = tag.string
        if tagStr == "Categories":
            tagStr = "Category:"
        if tagStr[-2:] == "s:":
            tagStr = f"{tagStr[:-2]}:"
        workTagHeaders.append(tagStr)
    del workTagHeadersRaw
    sqlInfo["rating"] = workTags[workTagHeaders.index("Rating:")].a.string
    sqlInfo["warnings"] = []
    sqlInfo["categories"] = []
    sqlInfo["tagsFandom"] = []
    sqlInfo["tagsShips"] = []
    sqlInfo["tagsChara"] = []
    sqlInfo["tagsOther"] = []
    for i in (
        ("warnings", "Archive Warning:", "Warnings!?!?!"),
        ("categories", "Category:", "Categories"),
        ("tagsFandom", "Fandom:", "Fandom Tags?!?!"),
        ("tagsShips", "Relationship:", "Ship Tags"),
        ("tagsChara", "Character:", "Character Tags"),
        ("tagsOther", "Additional Tag:", "General Tags"),
    ):
        try:
            for tag in workTags[workTagHeaders.index(i[1])].find_all("a"):
                sqlInfo[i[0]].append(tag.string)
        except ValueError:
            logger.debug(f"Work [{workID}] doesn't seem to have any [{i[2]}]")
    statsSplit = workTags[workTagHeaders.index("Stat:")].string.split()
    chapterNOs = statsSplit[statsSplit.index("Chapters:") + 1].split("/")
    sqlInfo["nchapters"] = int(chapterNOs[0])
    try:
        sqlInfo["chaptersExpected"] = int(chapterNOs[1])
    except ValueError:
        sqlInfo["chaptersExpected"] = 0
    dateUpdatedKey = "Updated:"
    if sqlInfo["chaptersExpected"] == 1:
        dateUpdatedKey = "Published:"
    elif sqlInfo["chaptersExpected"] == sqlInfo["nchapters"]:
        dateUpdatedKey = "Completed:"
    sqlInfo["dateUp"] = int(
        datetime.datetime.fromisoformat(
            statsSplit[1 + statsSplit.index(dateUpdatedKey)]
        ).timestamp()
    )
    sqlInfo["datePb"] = int(
        datetime.datetime.fromisoformat(
            statsSplit[1 + statsSplit.index("Published:")]
        ).timestamp()
    )
    allComments = rawSoup.find_all(string=lambda text: isinstance(text, bs4.Comment))
    sqlInfo["dateDl"] = 0
    sqlInfo["dateEd"] = 0
    for comment in allComments:
        for i in (
            (constants.commentTimestampDownloaded, "dateDl"),
            (constants.commentTimestampEdited, "dateEd"),
        ):
            if comment.find(i[0]) != -1:
                sqlInfo[i[1]] = int(
                    datetime.datetime.fromisoformat(comment[len(i[0]):]).timestamp()
                )
    if not sqlInfo["dateDl"]:
        logger.info(
            f"Raw [{workID}] doesn't seem to have a 'last downloaded' timestamp"
        )
    if not sqlInfo["dateEd"]:
        logger.info(f"Raw [{workID}] doesn't seem to have a 'last edited' timestamp")
    tagToFile(
        tag=tagsDiv,
        filename=os.path.join(wIdFolder, "tags.html"),
    )
    del tagsDiv
    ################################
    # Rest of Header
    ################################
    sqlInfo["title"] = headerMeta.h1.string
    headerBlockquotes = headerMeta.find_all("blockquote", class_="userstuff")
    try:
        tagToFile(
            tag=headerBlockquotes[1].contents,
            filename=os.path.join(wIdFolder, "start-notes.html"),
        )
        tagToFile(
            tag=headerBlockquotes[0].contents,
            filename=os.path.join(wIdFolder, "summary.html"),
        )
    except IndexError:
        match headerMeta.p.string:
            case "Summary":
                hbqDest = "summary.html"
            case "Notes":
                hbqDest = "start-notes.html"
        tagToFile(
            tag=headerBlockquotes[0].contents,
            filename=os.path.join(wIdFolder, hbqDest),
        )
        del hbqDest
    sqlInfo["authors"] = []
    for tag in headerMeta.div.find_all("a"):
        sqlInfo["authors"].append(tag.string)
    try:
        tagToFile(
            tag=rawSoup.find(id="afterword").find(id="endnotes").blockquote.contents,
            filename=os.path.join(wIdFolder, "end-notes.html"),
        )
    except AttributeError:
        logger.debug(f"Work [{workID}] doesn't seem to have work end notes/")
    db.addWork(
        id=workID,
        info=sqlInfo,
        config=config,
        logger=logger,
    )


def multithreading(
    workIDs: set,
    config: dict,
    logger: logging.Logger,
) -> None:
    if (len(workIDs) < 10) or (platform.system() == "Windows"):
        for workID in workIDs:
            processSingle(
                workID=workID,
                config=config,
                logger=logger,
            )
    else:
        import concurrent.futures

        futures = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            for workID in workIDs:
                futures[workID] = pool.submit(
                    processSingle, workID=workID, config=config, logger=logger
                )


if __name__ == "__main__":
    workIDs = set(())
    for line in init.args.infile:
        try:
            workIDs.add(int(str(line).strip()))
        except ValueError:
            init.errLogger.error(
                f"Could not convert input [{str(line).strip()}] to int"
            )
    multithreading(
        workIDs=workIDs,
        config=init.config,
        logger=init.logger,
    )
