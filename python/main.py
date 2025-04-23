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
) -> set:
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
    else:
        network.downloadWork(work=work, filename=filename, logger=logger)

    work.load_chapters()
    soup, setErrImg = format.main(work=work, raw=filename, logger=logger, config=config)
    outFileFull = f"{config['dirOutput']}/{config['dirOutHtml']}/{raws.getPrefferedFilenameFromWorkID(id=work.id, logger=logger)}"
    with open(
        file=outFileFull,
        mode="w",
    ) as out:
        out.write(soup.prettify(formatter="html5"))

    if os.path.getsize(outFileFull) < os.path.getsize(filename):
        logger.error(f"Work {work.id} Output file is smaller than raw file.")

    try:
        work.workskin
    except AttributeError:
        logger.debug(
            "You're using a version of ao3_api that doesn't yet support Workskin downloading."
        )
    else:
        with open(
            raws.getPrefferedFilenameFromWorkID(
                id=work.id, logger=logger, extension=".css"
            )
        ) as cssOut:
            cssOut.write(work.workskin)

    if rowDB:
        database.updateWork(
            id=work.id, filename=config["dbFileFull"], row=rowLive, logger=logger
        )
    else:
        database.newWork(
            id=work.id, filename=config["dbFileFull"], row=rowLive, logger=logger
        )

    return setErrImg


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

    session = network.login(config=config, logger=logger)
    for i in batch.parseBatchLine(
        line=settings.args.input,
        logger=logger,
    ):
        workID = i
        break
    work = network.getWorkObjFromId(
        id=workID,
        logger=logger,
        session=session,
        load_chapters=False,
    )
    if work is False:
        raise Exception

    if not os.path.exists(config["dbFileFull"]):
        database.initDB(filename=config["dbFileFull"], logger=logger)
    setErrImg = main(work=work, config=config, logger=logger)
    with open(f"{config['dirLogs']}/err-main-imgIncomplete.log", "w") as fileErrImg:
        for i in setErrImg:
            fileErrImg.write(f"{i}\n")
    if config["useGit"]:
        acp(dirRaws=config["dirRaws"], logger=logger)
    logger.info("Complete, main.py stopping")
