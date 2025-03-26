#!/usr/bin/env python3

import datetime
import logging
import os.path

import AO3

import database
import format
import getLogger
import network
import raws
import settings


def parseInput(
    input: str,
    logger: logging.Logger,
):
    try:
        id = int(input.strip())
    except ValueError:
        id = AO3.utils.workid_from_url(input)
    if not id:
        raise Exception(f"Invalid input to main() in main.py: {input}")
    return id


def main(
    work: AO3.works.Work,
    config: dict,
    logger: logging.Logger,
    forceDownloadNew=False,
):
    filename = f"{config['dirRaws']}/{raws.getPrefferedFilenameFromWorkID(id=work.id, logger=logger)}"
    rowLive = database.workToRow(work=work)
    if os.path.exists(filename) and not forceDownloadNew:
        rowFile = raws.getRowFromFilename(filename=filename, logger=logger)
        if raws.checkUpdates(
            row1=rowFile.__dict__,
            row2=rowLive.__dict__,
        ):
            network.downloadWork(work=work, filename=filename, logger=logger)
    else:
        network.downloadWork(work=work, filename=filename, logger=logger)
    rowDB = database.getRow(ID=work.id, filename=config["dbFileFull"], logger=logger)
    if not rowDB:
        rowDB = rowLive
        rowDB.dateLastDownloaded = (
            datetime.datetime.now().astimezone().replace(microsecond=0)
        )
        rowDB.titleOG = rowDB.title
        rowDB.chaptersCountOG = rowDB.chaptersCount
        rowDB.chaptersExpectedOG = rowDB.chaptersExpected
        rowDB.dateFirstDownloaded = rowDB.dateLastDownloaded

    soup = format.main(work=work, raw=filename, logger=logger, config=config)
    with open(
        file=f"{config['dirOutput']}/{config['dirOutHtml']}/{raws.getPrefferedFilenameFromWorkID(id=work.id, logger=logger)}",
        mode="w",
    ) as out:
        out.write(soup.prettify(formatter="html5"))

    database.putRow(ID=work.id, filename=config["dbFileFull"], row=rowDB, logger=logger)


if __name__ == "__main__":
    settings.setup()
    settings.parser.add_argument("input")
    settings.parse()
    config = settings.settings

    logCore = "main"
    if config["logsTimestamp"]:
        logAppend = (
            datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
        )
    else:
        logAppend = "latest"
    logger = getLogger.getLogger(
        core=logCore,
        append=logAppend,
        dirLogs=config["dirLogs"],
    )

    if config["ao3DoLogin"]:
        with open(config["ao3UsernameFile"]) as file:
            ao3Username = file.readline().strip()
        with open(config["ao3PasswordFile"]) as file:
            ao3Password = file.readline().strip()
        session = network.getSessionObj(
            username=ao3Username, password=ao3Password, logger=logger
        )
        del ao3Username
        del ao3Password
    else:
        session = None
    work = network.getWorkObjFromId(
        id=parseInput(input=settings.args.input, logger=logger),
        logger=logger,
        session=session,
        load_chapters=False,
    )

    if not os.path.exists(config["dbFileFull"]):
        database.initDB(filename=config["dbFileFull"], logger=logger)
    work.load_chapters()
    main(work=work, config=config, logger=logger)
