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
    logger: logging.Logger,
) -> None:
    if isinstance(tag, str):
        tagStr = tag
    if isinstance(tag, list):
        tagStr = ""
        for i in tag:
            try:
                tagStr += i.prettify(formatter="html5")
            except AttributeError:
                logger.log(
                    int(30 - (20 * int(isinstance(i, bs4.NavigableString)))),
                    f"tagToFile() encountered [{type(i)}] which doesn't have a 'prettify' method",
                )
                tagStr += str(i)
    if isinstance(tag, bs4.Tag):
        tagStr = tag.prettify(formatter="html5")
    with open(filename, "w") as file:
        file.write(tagStr)


def processSingle(
    workID: int,
    config: dict,
    logger: logging.Logger,
) -> None:
    logger.info(f"Started Processing [{workID}]")
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
    del chapterNOs
    sqlInfo["dateUp"] = 0
    for i in ("Completed:", "Updated:", "Published"):
        if not sqlInfo["dateUp"]:
            try:
                sqlInfo["dateUp"] = int(
                    datetime.datetime.fromisoformat(
                        statsSplit[1 + statsSplit.index(i)]
                    ).timestamp()
                )
            except ValueError:
                pass
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
        logger=logger,
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
            logger=logger,
        )
        tagToFile(
            tag=headerBlockquotes[0].contents,
            filename=os.path.join(wIdFolder, "summary.html"),
            logger=logger,
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
            logger=logger,
        )
        del hbqDest
    sqlInfo["authors"] = []
    for tag in headerMeta.div.find_all("a"):
        sqlInfo["authors"].append(tag.string)
    try:
        tagToFile(
            tag=rawSoup.find(id="afterword").find(id="endnotes").blockquote.contents,
            filename=os.path.join(wIdFolder, "end-notes.html"),
            logger=logger,
        )
    except AttributeError:
        logger.debug(f"Work [{workID}] doesn't seem to have work end notes")
    allPrefaces = rawSoup.select("#chapters > div.meta.group")
    allMains = rawSoup.select("#chapters > div.userstuff")
    allPostfaces = {}
    for i in range(1, 1 + len(allMains)):
        try:
            allPostfaces[i] = rawSoup.find(id=f"endnotes{i}")
        except KeyError:
            logger.debug(f"Work [{workID}] Chapter [{i}] doesn't seem to have endnotes")
    logger.debug(
        f"Pref/Main/Post for [{workID}]: [{len(allPrefaces)}] [{len(allMains)}] [{len(allPostfaces)}]"
    )
    for chaptNum in range(1, 1 + len(allMains)):
        chaptFolder = os.path.join(wIdFolder, str(chaptNum))
        os.makedirs(chaptFolder, exist_ok=True)
        ################################
        # Real
        ################################
        if len(allPrefaces) != 0:
            tagToFile(
                tag=allPrefaces[chaptNum - 1].h2.string,
                filename=os.path.join(chaptFolder, "title.txt"),
                logger=logger,
            )
            preBQs = allPrefaces[chaptNum - 1].find_all("blockquote")
            if len(preBQs) == 2:
                tagToFile(
                    tag=preBQs[0].contents,
                    filename=os.path.join(chaptFolder, "summary.html"),
                    logger=logger,
                )
                tagToFile(
                    tag=preBQs[1].contents,
                    filename=os.path.join(chaptFolder, "notes-start.html"),
                    logger=logger,
                )
            elif len(preBQs) == 1:
                pCandidates = allPrefaces[chaptNum - 1].select("div.meta.group > p")
                match pCandidates[-1].string:
                    case "Chapter Notes":
                        bqDest = "notes-start.html"
                    case "Chapter Summary":
                        bqDest = "summary.html"
                tagToFile(
                    tag=preBQs[0].contents,
                    filename=os.path.join(chaptFolder, bqDest),
                    logger=logger,
                )
                del pCandidates
                del bqDest
            del preBQs
        elif len(allMains) == 1 and sqlInfo["nchapters"] == 1:
            logger.debug(f"Work [{workID}] seems to be a oneshot")
        else:
            logger.error(
                f"Work [{workID}], which doesn't seem to be a oneshot, had a len(allPrefaces) of 0"
            )
        tagToFile(
            tag=allMains[chaptNum - 1].contents,
            filename=os.path.join(chaptFolder, "main.html"),
            logger=logger,
        )
        tail = allPostfaces.get(chaptNum)
        if tail:
            tagToFile(
                tag=tail.blockquote.contents,
                filename=os.path.join(chaptFolder, "notes-end.html"),
                logger=logger,
            )

    db.addWork(
        id=workID,
        info=sqlInfo,
        config=config,
        logger=logger,
    )
    logger.info(f"Completed Processing [{workID}]")


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
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=10, thread_name_prefix=constants.threadNameBulk
        ) as pool:
            for workID in workIDs:
                futures[workID] = pool.submit(
                    processSingle, workID=workID, config=config, logger=logger
                )
        for i in futures:
            futures[i].result()
    logger.info("Complete, process.multithreding exiting")


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
