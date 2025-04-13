#!/usr/bin/env python3

import datetime
import logging
import os.path
import subprocess

import AO3

import batch
import database
import format
import getLogger
import network
import raws
import settings


def acp(
    dirRaws: str,
    logger: logging.Logger,
):
    for i in os.listdir(dirRaws):
        subprocess.run(["git", "-C", dirRaws, "add", i])
    subprocess.run(["git", "-C", dirRaws, "commit", "-m", "commit message"])
    subprocess.run(["git", "-C", dirRaws, "push"])


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

    if (
        os.path.exists(filename)
        and (os.path.getsize(filename))  # (bool(int)) equivilant to (int != 0)
        and (not forceDownloadNew)
    ):
        if raws.checkUpdates(
            row1=raws.getRowFromFilename(filename=filename, logger=logger),
            row2=rowLive,
        ):
            network.downloadWork(work=work, filename=filename, logger=logger)
            work.load_chapters()
    else:
        network.downloadWork(work=work, filename=filename, logger=logger)
        work.load_chapters()

    soup = format.main(work=work, raw=filename, logger=logger, config=config)
    outFileFull = f"{config['dirOutput']}/{config['dirOutHtml']}/{raws.getPrefferedFilenameFromWorkID(id=work.id, logger=logger)}"
    with open(
        file=outFileFull,
        mode="w",
    ) as out:
        out.write(soup.prettify(formatter="html5"))

    if os.path.getsize(outFileFull) < os.path.getsize(filename):
        logger.error(f"Work {work.id} Output file is smaller than raw file.")

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
    settings.input(
        helptext="WorkID of or link to work.",
        name="input",
    )
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
        level=config["logsLevel"],
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
        id=batch.parseBatchLine(
            line=settings.args.input,
            logger=logger,
        )[0],
        logger=logger,
        session=session,
        load_chapters=False,
    )
    if work is False:
        raise Exception

    if not os.path.exists(config["dbFileFull"]):
        database.initDB(filename=config["dbFileFull"], logger=logger)
    work.load_chapters()
    main(work=work, config=config, logger=logger)
    if config["useGit"]:
        acp(dirRaws=config["dirRaws"], logger=logger)
    logger.info("Complete, main.py stopping")
