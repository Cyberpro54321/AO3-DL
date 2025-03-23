#!/usr/bin/env python3

import datetime
import logging
import os.path
import sqlite3

import AO3


class row:
    def __init__(
        self,
        ID: int,
        title: str,
        chaptersCount: int,
        chaptersExpected: int,
        dateLastDownloaded: datetime.datetime,
        dateLastUpdated: datetime.datetime,
        checkForUpdates: bool = False,
        titleOG: str = "",
        chaptersCountOG: int = 0,
        chaptersExpectedOG: int = 0,
        dateFirstDownloaded: datetime.datetime = 0,
        dateLastEdited: datetime.datetime = 0,
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

    def __str__(self):
        return str(self.__dict__)

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


def workToRow(
    work: AO3.works.Work,
):
    return row(
        ID=work.id,
        title=work.title,
        chaptersCount=work.nchapters,
        chaptersExpected=int(work.expected_chapters or 0),
        dateLastDownloaded=0,
        dateLastUpdated=work.date_updated,
        dateLastEdited=work.date_edited,
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
    con, cur = openDB(filename=filename, logger=logger)
    res1 = cur.execute(f"SELECT * FROM works WHERE ID = {ID}")
    out = res1.fetchone()
    con.close()
    if out:
        return row(
            ID=out[0],
            title=out[1],
            chaptersCount=out[2],
            chaptersExpected=out[3],
            dateLastDownloaded=out[4],
            titleOG=out[5],
            chaptersCountOG=out[6],
            chaptersExpectedOG=out[7],
            dateFirstDownloaded=out[8],
            dateLastEdited=out[9],
            dateLastUpdated=out[10],
            checkForUpdates=out[11],
        )


def getWorkIdSet(
    filename: str,
    logger: logging.Logger,
):
    con, cur = openDB(filename=filename, logger=logger)
    res1 = cur.execute("SELECT ID FROM works")
    allIDs = res1.fetchall()
    con.close()
    ids = set(())
    for i in allIDs:
        ids.add(i[0])
    return ids
