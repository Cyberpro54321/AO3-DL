#!/usr/bin/env python3

version = "Rapid Development"
workIdMaxDigits = 8  # Maximum number of digits long an AO3 WorkID might be. at the moment you can probably leave this at 8 and it'll be just fine
loopRetries = 100  # How many times to retry doing an action that sometimes fails (ie downloading a work) before giving up and throwing an exception
loopErrorTemplate = "Experienced {2} while {0}, sleeping for {1} seconds before retrying. Arguments: {3!r}"
ao3WorksPerSeriesPage = 20
threadNameBulk = "worker"

stylesheetsListShort = [
    ["screen", "1_site_screen_.css"],
    [
        "only screen and (max-width: 62em), handheld",
        "4_site_midsize.handheld_.css",
    ],
    [
        "only screen and (max-width: 42em), handheld",
        "5_site_narrow.handheld_.css",
    ],
    ["speech", "6_site_speech_.css"],
    ["print", "7_site_print_.css"],
]
stylesheetsListLong = [
    ["screen", "01-core.css"],
    ["screen", "02-elements.css"],
    ["screen", "03-region-header.css"],
    ["screen", "04-region-dashboard.css"],
    ["screen", "05-region-main.css"],
    ["screen", "06-region-footer.css"],
    ["screen", "07-interactions.css"],
    ["screen", "08-actions.css"],
    ["screen", "09-roles-states.css"],
    ["screen", "10-types-groups.css"],
    ["screen", "11-group-listbox.css"],
    ["screen", "12-group-meta.css"],
    ["screen", "13-group-blurb.css"],
    ["screen", "14-group-preface.css"],
    ["screen", "15-group-comments.css"],
    ["screen", "16-zone-system.css"],
    ["screen", "17-zone-home.css"],
    ["screen", "18-zone-searchbrowse.css"],
    ["screen", "19-zone-tags.css"],
    ["screen", "20-zone-translation.css"],
    ["screen", "21-userstuff.css"],
    ["screen", "22-system-messages.css"],
    ["only screen and (max-width: 62em), handheld", "25-media-midsize.css"],
    ["only screen and (max-width: 42em), handheld", "26-media-narrow.css"],
    ["speech", "27-media-aural.css"],
    ["print", "28-media-print.css"],
]
