#!/usr/bin/env python3
# import concurrent.futures
import logging
import os.path
import platform

import bs4

import init


def tagToFile(
    tag: bs4.Tag,
    filename: str,
) -> None:
    newSoup = bs4.BeautifulSoup()
    newSoup.append(tag)
    with open(filename, "w") as file:
        file.write(newSoup.prettify(formatter="html5"))


def processSingle(
    workID: int,
    config: dict,
    logger: logging.Logger,
) -> None:
    logger.info(workID)
    with open(os.path.join(config["dirRaws"], f"{workID:0>8}.html")) as rawFile:
        rawSoup = bs4.BeautifulSoup(rawFile, features="lxml")
    wIdFolder = os.path.join(config["dirOut"], f"{workID:0>8}")
    if not os.path.exists(wIdFolder):
        os.mkdir(wIdFolder)
    if (not os.path.isdir(wIdFolder)) or (not os.path.exists(wIdFolder)):
        raise Exception

    tagsDiv = rawSoup.find(id="preface").div.dl
    tagsDiv["class"] = ["works meta group"]
    tagToFile(
        tag=tagsDiv,
        filename=os.path.join(wIdFolder, "tags.html"),
    )
    del tagsDiv


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
