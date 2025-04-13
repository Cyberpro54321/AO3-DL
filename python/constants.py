#!/usr/bin/env python3

version = "Rapid Development"
workIdMaxDigits = 8  # Maximum number of digits long an AO3 WorkID might be. at the moment you can probably leave this at 8 and it'll be just fine
loopRetries = 100  # How many times to retry doing an action that sometimes fails (ie downloading a work) before giving up and throwing an exception
loopErrorTemplate = "Experienced {2} while {0}, sleeping for {1} seconds before retrying. Arguments:\n{3!r}"
ao3WorksPerSeriesPage = 20
threadNameBulk = "worker"
