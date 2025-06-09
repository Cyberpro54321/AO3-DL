import datetime
import logging

import sqlWrapper


def addWork(
    id: int,
    info: dict,
    config: dict,
    logger: logging.Logger,
):
    try:
        for i in (
            ("title", str),
            ("nchapters", int),
            ("chaptersExpected", int),
            ("dateDl", int),
            ("dateEd", int),
            ("dateUp", int),
            ("datePb", int),
            ("rating", str),
            ("warnings", list),
            ("categories", list),
            ("authors", list),
            ("tagsFandom", list),
            ("tagsShips", list),
            ("tagsChara", list),
            ("tagsOther", list),
        ):
            if not isinstance(info[i[0]], i[1]):
                raise KeyError
    except KeyError:
        exceptionStr = "Invalid info dict given to addWork() in db.py"
        logger.critical(exceptionStr)
        raise Exception(exceptionStr)
    sqlStr = ""
    sqlStr = "INSERT OR REPLACE INTO works VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    sqlTpl = (
        id,
        info["title"],
        info["nchapters"],
        info["chaptersExpected"],
        info["dateDl"],
        info["dateEd"],
        info["dateUp"],
        info["datePb"],
        int(datetime.datetime.now().astimezone().replace(microsecond=0).timestamp()),
    )
    sqlWrapper.execute(
        string=sqlStr,
        config=config,
        logger=logger,
        args=sqlTpl,
    )
    del sqlStr
    del sqlTpl

    ratingInt = 0
    ratings = [
        "Not Rated",
        "General Audiences",
        "Teen And Up Audiences",
        "Mature",
        "Explicit",
    ]
    ratingInt = ratings.index(info["rating"]) + 1

    warningInt = 0
    warnings = [
        "No Archive Warnings Apply",
        "Graphic Depictions Of Violence",
        "Major Character Death",
        "Rape/Non-Con",
        "Underage Sex",
        "Creator Chose Not To Use Archive Warnings",
    ]
    for i in info["warnings"]:
        warningInt += pow(2, warnings.index(i))

    categoryInt = 0
    categoriesList = [
        "F/F",
        "F/M",
        "Gen",
        "M/M",
        "Multi",
        "Other",
    ]
    for i in info["categories"]:
        categoryInt += pow(2, categoriesList.index(i))

    authorStr = ""
    for author in info["authors"]:
        if authorStr:
            authorStr += ", "
        authorStr += author

    sqlStr = "INSERT OR REPLACE INTO tags VALUES (?, ?, ?, ?, ?"
    for i in range(75 * 4):
        sqlStr += ", ?"
    sqlStr += ")"
    sqlTpl = (
        id,
        ratingInt,
        warningInt,
        categoryInt,
        authorStr,
    )

    for i in (
        info["tagsFandom"],
        info["tagsShips"],
        info["tagsChara"],
        info["tagsOther"],
    ):
        while len(i) > 75:
            i.pop(75)
        while len(i) < 75:
            i.append("")
        sqlTpl += tuple(i)

    sqlWrapper.execute(
        string=sqlStr,
        config=config,
        logger=logger,
        args=sqlTpl,
    )
