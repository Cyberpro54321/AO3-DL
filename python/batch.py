#!/usr/bin/env python3

import logging

import AO3

import constants
import network


def parseBatchFile(
    file: str,
    logger: logging.Logger,
    ao3Session: AO3.Session = None,
) -> set:
    ids = set(())
    lines = set(())
    with open(file) as inputFile:
        for line in inputFile:
            lines.add(line.strip())
    for line in lines:
        for id in parseBatchLine(line=line, logger=logger, ao3Session=ao3Session):
            ids.add(id)
    return ids


def parseBatchLine(
    line: str,
    logger: logging.Logger,
    ao3Session: AO3.Session = None,
) -> set:
    ids = set(())
    try:
        ids.add(int(line.strip()))
    except ValueError:
        split = line.split("/")
        indexW = 0
        indexS = 0
        try:
            indexW = split.index("works") + 1
        except ValueError:
            try:
                indexS = split.index("series") + 1
            except ValueError:
                raise Exception()
        if indexW and len(split) >= indexW:
            id = split[indexW].split("?")[0]
            if id.isdigit():
                ids.add(id)
        elif indexS and len(split) >= indexS:
            id = split[indexS].split("?")[0]
            series = network.getSeriesObj(
                seriesID=id, logger=logger, ao3Session=ao3Session
            )
            for id in getWorkIdsFromSeriesObj(
                series=series, logger=logger, ao3Session=ao3Session
            ):
                ids.add(id)
    return ids


def getWorkIdsFromSeriesObj(
    series: AO3.Series,
    logger: logging.Logger,
    ao3Session: AO3.Session = None,
) -> set:
    pagesSet = divmod(series.nworks, constants.ao3WorksPerSeriesPage)
    pagesCount = pagesSet[0] + int(bool(pagesSet[1]))
    ids = set(())
    for i in series.work_list:
        ids.add(i.id)
    if pagesCount != 1 and len(ids) == constants.ao3WorksPerSeriesPage:
        for i in range(2, pagesCount + 1):
            seriesX = network.getSeriesObj(
                seriesID=f"{series.id}?page={i}",
                logger=logger,
                ao3Session=ao3Session,
            )
            for j in seriesX.work_list:
                ids.add(j.id)
    return ids
