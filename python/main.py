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
    if os.path.exists(config["dbFileFull"]):
        rowDB = database.getWork(
            id=work.id, filename=config["dbFileFull"], logger=logger
        )
    else:
        database.initDB(filename=config["dbFileFull"], logger=logger)
        rowDB = False

    if os.path.exists(filename) and not forceDownloadNew:
        if raws.checkUpdates(
            row1=raws.getRowFromFilename(filename=filename, logger=logger),
            row2=rowLive,
        ):
            network.downloadWork(work=work, filename=filename, logger=logger)
    else:
        network.downloadWork(work=work, filename=filename, logger=logger)

    soup = format.main(work=work, raw=filename, logger=logger, config=config)
    with open(
        file=f"{config['dirOutput']}/{config['dirOutHtml']}/{raws.getPrefferedFilenameFromWorkID(id=work.id, logger=logger)}",
        mode="w",
    ) as out:
        out.write(soup.prettify(formatter="html5"))

    if rowDB:
        database.updateWork(
            id=work.id, filename=config["dbFileFull"], row=rowLive, logger=logger
        )
    else:
        database.newWork(
            id=work.id, filename=config["dbFileFull"], row=rowLive, logger=logger
        )


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
