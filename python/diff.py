#!/usr/bin/env python3

import argparse
import logging

import batch

parser = argparse.ArgumentParser()
parser.add_argument("--existing")
parser.add_argument("--new")
parser.add_argument("--out")
args = parser.parse_args()

logger = logging.Logger
setNew = batch.parseBatchFile(file=args.new, logger=logger)
setOld = batch.parseBatchFile(file=args.existing, logger=logger)

setOut = setNew.difference(setOld)
with open(args.out, "w") as out:
    for i in setOut:
        out.write(f"{i}\n")
