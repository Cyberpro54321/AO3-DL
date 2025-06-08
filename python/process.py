#!/usr/bin/env python3
# import concurrent.futures
import logging
import platform

import init


def processSingle(
    workID: int,
    logger: logging.Logger,
) -> None:
    logger.info(workID)


def multithreading(
    workIDs: set,
    logger: logging.Logger,
) -> None:
    if (len(workIDs) < 10) or (platform.system() == "Windows"):
        for workID in workIDs:
            processSingle(
                workID=workID,
                logger=logger,
            )
    else:
        import concurrent.futures

        futures = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            for workID in workIDs:
                futures[workID] = pool.submit(processSingle, workID, logger)


if __name__ == "__main__":
    workIDs = set(())
    for line in init.args.infile:
        try:
            workIDs.add(int(str(line).strip()))
        except ValueError:
            init.errLogger.error(
                f"Could not convert input [{str(line).strip()}] to int"
            )
    multithreading(workIDs=workIDs, logger=init.logger)
