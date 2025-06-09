import logging


initStrWorks = """
CREATE TABLE IF NOT EXISTS works(
ID INTEGER PRIMARY KEY,
title VARCHAR(256),
chaptersCount INTEGER,
chaptersExpected INTEGER,
dateLastDownloaded INTEGER,
dateLastEdited INTEGER,
dateLastUpdated INTEGER,
datePublished INTEGER,
dateProcessed INTEGER);"""
initStrTags = """
CREATE TABLE IF NOT EXISTS tags(
ID INTEGER PRIMATY KEY,
rating INTEGER,
warnings INTEGER,
category INTEGER,
authorStr VARCHAR(420)
"""
for tagType in (
    "Fandom",
    "Ship",
    "Character",
    "Freeform",
):
    for i in range(75):
        initStrTags += f", tag{tagType}{i + 1} VARCHAR(100)"
initStrTags = initStrTags + ");"


def execute(
    string: str,
    config: dict,
    logger: logging.Logger,
    args: tuple = (),
    firstAttempt: bool = True,
) -> bool:
    try:
        config["sqlType"]
        config["sqlLocation"]
    except KeyError:
        raise Exception
    match config["sqlType"]:
        case "sqlite":
            import os.path
            import sqlite3

            try:
                con = sqlite3.connect(
                    os.path.join(config["dirOut"], config["sqlLocation"])
                )
                cur = con.cursor()
                logger.debug(string)
                if args:
                    logger.debug(args)
                    cur.execute(string, args)
                else:
                    cur.execute(string)
                con.commit()
                con.close()
            except sqlite3.OperationalError:
                if string in (initStrWorks, initStrTags):
                    exceptionStr = (
                        "Getting sqlite3.OperationalError while initializing database"
                    )
                    logger.critical(exceptionStr)
                    raise Exception(exceptionStr)
                elif firstAttempt:
                    execute(string=initStrWorks, config=config, logger=logger)
                    execute(string=initStrTags, config=config, logger=logger)
                    execute(
                        string=string,
                        config=config,
                        logger=logger,
                        args=args,
                        firstAttempt=False,
                    )
                else:
                    exceptionStr = "Got sqlite3.OperationalError after confirming db initialization"
                    logger.critical(exceptionStr)
                    raise Exception(exceptionStr)
        case _:
            exceptionStr = (
                f"Invalid sqlType given to sqlWrapper() [{config['sqlType']}]"
            )
            logger.critical(exceptionStr)
            raise Exception(exceptionStr)
