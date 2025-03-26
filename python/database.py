#!/usr/bin/env python3

import datetime
import logging
import os.path
import sqlite3

import AO3


# id: int,
# title: str,
# chaptersCount: int,
# chaptersExpected: int,
# dateLastDownloaded: datetime.datetime,
# dateLastUpdated: datetime.datetime,
# titleOG: str = "",
# chaptersCountOG: int = 0,
# chaptersExpectedOG: int = 0,
# dateFirstDownloaded: datetime.datetime = 0,
# dateLastEdited: datetime.datetime = 0,


def workToRow(
    work: AO3.works.Work,
):
    return {
        "id": work.id,
        "title": work.title,
        "chaptersCount": work.nchapters,
        "chaptersExpected": int(work.expected_chapters or 0),
        "dateLastDownloaded": 0,
        "dateLastUpdated": work.date_updated,
        "dateLastEdited": work.date_edited,
    }


def openDB(
    filename: str,
    logger: logging.Logger,
) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    con = sqlite3.connect(
        filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    cur = con.cursor()
    return con, cur


def initDB(
    filename: str,
    logger: logging.Logger,
) -> None:
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
        dateLastUpdated TIMESTAMP);"""
    )
    con.commit()
    con.close()


# def putRow(
#     ID: int,
#     filename: str,
#     row: dict,
#     logger: logging.Logger = logging.getLogger(__name__),
# ):
#     if not os.path.exists(filename):
#         initDB(filename=filename, logger=logger)
#     insertString = (
#         "INSERT OR REPLACE INTO works VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
#     )
#     con, cur = openDB(filename=filename, logger=logger)
#     cur.execute(insertString, row.toTuple())
#     con.commit()
#     con.close()


def newWork(
    id: int,
    filename: str,
    row: dict,
    logger: logging.Logger,
):
    if id != row["id"]:
        raise Exception
    con, cur = openDB(filename=filename, logger=logger)
    insertString = "INSERT INTO works VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    insertTuple = tuple(
        id,
        row["title"],
        row["chaptersCount"],
        row["chaptersExpected"],
        row["dateLastDownloaded"],
        row["title"],
        row["chaptersCount"],
        row["chaptersExpected"],
        row["dateLastDownloaded"],
        row["dateLastEdited"],
        row["dateLastUpdated"],
    )
    cur.execute(insertString, insertTuple)
    con.commit()
    con.close()


def updateWork(
    id: int,
    filename: str,
    row: dict,
    logger: logging.Logger,
):
    if id != row["id"]:
        raise Exception
    con, cur = openDB(filename=filename, logger=logger)
    updateString = f"""
    UPDATE works
    SET title = {row['title']}
    SET chaptersCount = {row['chaptersCount']}
    SET chaptersExpected = {row['chaptersExpected']}
    SET dateLastDownloaded = {row['dateLastDownloaded']}
    SET dateLastEdited = {row['dateLastEdited']}
    SET dateLastUpdated = {row['dateLastUpdated']}
    WHERE ID = {id};
    """
    cur.execute(updateString)
    con.commit()
    con.close()


def getWork(
    id: int,
    filename: str,
    logger: logging.Logger,
) -> dict | bool:
    con, cur = openDB(filename=filename, logger=logger)
    res1 = cur.execute(
        f"SELECT title, chaptersCount, chaptersExpected, dateLastDownloaded, dateLastEdited, dateLastUpdated FROM works WHERE ID = {id}"
    )
    out = res1.fetchone()
    con.close()
    if out:
        return {
            "id": id,
            "title": out[0],
            "chaptersCount": out[1],
            "chaptersExpected": out[2],
            "dateLastDownloaded": out[3],
            "dateLastEdited": out[4],
            "dateLastUpdated": out[5],
        }
    else:
        return False


def getWorkIdSet(
    filename: str,
    logger: logging.Logger,
) -> set:
    con, cur = openDB(filename=filename, logger=logger)
    res1 = cur.execute("SELECT ID FROM works")
    allIDs = res1.fetchall()
    con.close()
    ids = set(())
    for i in allIDs:
        ids.add(i[0])
    return ids
