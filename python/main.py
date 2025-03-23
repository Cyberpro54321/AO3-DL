#!/usr/bin/env python3

import datetime
import logging

import AO3

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
    downloadNew: bool = True,
):
    # TODO: Check if raw file exists. If raw file doesn't exist or is outdated, download new one

    # Formatting

    # Update Database
    pass


if __name__ == "__main__":
    settings.setup()
    settings.parser.add_argument("input")
    settings.parse()
    config = settings.settings

    logger = logging.getLogger(__name__)
    if config["logsTimestamp"]:
        logName = f"main-{datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()}"
    else:
        logName = "main-latest"
    logging.basicConfig(
        filename=f"{config['dirLogs']}/{logName}.log",
        filemode="w",
        encoding="utf-8",
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)-8s]: %(message)s",
        datefmt="%H:%M:%S",
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

    main(work=work, config=config, logger=logger)
