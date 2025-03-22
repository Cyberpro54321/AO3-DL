import sqlite3
import datetime
import logging
import os.path


class row:
    def __init__(
        self,
        ID: int,
        title: str,
        chaptersCount: int,
        chaptersExpected: int,
        dateLastDownloaded: datetime.datetime,
        titleOG: str,
        chaptersCountOG: int,
        chaptersExpectedOG: int,
        dateFirstDownloaded: datetime.datetime,
        dateLastEdited: datetime.datetime,
        dateLastUpdated: datetime.datetime,
        checkForUpdates: bool,
    ):
        self.ID = ID
        self.title = title
        self.chaptersCount = chaptersCount
        self.chaptersExpected = chaptersExpected
        self.dateLastDownloaded = dateLastDownloaded
        self.titleOG = titleOG
        self.chaptersCountOG = chaptersCountOG
        self.chaptersExpectedOG = chaptersExpectedOG
        self.dateFirstDownloaded = dateFirstDownloaded
        self.dateLastEdited = dateLastEdited
        self.dateLastUpdated = dateLastUpdated
        self.checkForUpdates = checkForUpdates

    def toTuple(self):
        return (
            self.ID,
            self.title,
            self.chaptersCount,
            self.chaptersExpected,
            self.dateLastDownloaded,
            self.titleOG,
            self.chaptersCountOG,
            self.chaptersExpectedOG,
            self.dateFirstDownloaded,
            self.dateLastEdited,
            self.dateLastUpdated,
            self.checkForUpdates,
        )


def openDB(
    filename: str,
    logger: logging.Logger,
):
    con = sqlite3.connect(
        filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    cur = con.cursor()
    return con, cur


def initDB(
    filename: str,
    logger: logging.Logger,
):
    con, cur = openDB(filename=filename, logger=logger)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS works(
        ID INTEGER PRIMARY KEY,
        title VARCHAR(256),
        chaptersCount INTEGER,
        chaptersExpected INTEGER,
        dateLastDownloaded TIMESTAMP,
        titleOG VARCHAR(256),
        chaptersCountOG INTEGER,
        chaptersExpectedOG INTEGER,
        dateFirstDownloaded TIMESTAMP,
        dateLastEdited TIMESTAMP,
        dateLastUpdated TIMESTAMP,
        checkForUpdates BOOL);"""
    )
    con.commit()
    con.close()


def putRow(
    ID: int,
    filename: str,
    row: row,
    logger: logging.Logger = logging.getLogger(__name__),
):
    if not os.path.exists(filename):
        initDB(filename=filename, logger=logger)
    insertString = (
        "INSERT OR REPLACE INTO works VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    con, cur = openDB(filename=filename, logger=logger)
    cur.execute(insertString, row.toTuple())
    con.commit()
    con.close()


def getRow(
    ID: int,
    filename: str,
    logger: logging.Logger,
):
    pass
