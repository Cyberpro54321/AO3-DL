#!/usr/bin/env python3

import os.path
import subprocess

import init

config = init.config

cautiousMode = False


def abspath(input: str) -> str:
    return os.path.abspath(os.path.expanduser(input))


def getbool(prompt: str) -> bool:
    yesValues = ["yes", "y", "true", "t", "go", "continue"]
    noValues = ["no", "n", "false", "f", "cancel", "stop"]
    if prompt[-1:] != "\n":
        prompt += "\n"
    loopno = 0
    while True:
        loopno += 1
        text = input(prompt).lower()
        if len(text) == 0:
            text = " "
        if text in yesValues:
            return True
        elif text in noValues:
            return False

        if loopno > 3:
            print(f"Valid options that mean 'yes' are: {yesValues}")
            print(f"Valid options that mean 'no' are: {noValues}")


for i in (
    config["dirRaws"],
    os.path.join(config["dirOut"], "ao3css"),
    os.path.dirname(config["ao3UsernameFile"]),
    os.path.dirname(config["ao3PasswordFile"]),
    os.path.dirname(config["ao3SessionPickle"]),
):
    os.makedirs(i, exist_ok=True)


copiedFiles = (
    ("config.ini", "./"),
    ("list.css", "../docker/"),
    ("list.php", "../docker/"),
    ("work.php", "../docker/"),
    ("index.html", "../docker/"),
)


needCopyFiles = False
for i in copiedFiles:
    target = os.path.join(abspath(config["dirOut"]), i[0])
    if not os.path.exists(target):
        needCopyFiles = True
    elif not os.path.getsize(target):
        needCopyFiles = True


if needCopyFiles:
    doCopyLoop = True
    while doCopyLoop:
        doCopy = getbool(
            f"Will now copy the following files to {config['dirOut']}:\n{[x[0] for x in copiedFiles]}\nEnter Yes to continue or No to stop."
        )
        if doCopy:
            doCopyLoop = False
        else:
            raise Exception("Operation canceled by user.")
    for i in copiedFiles:
        local = abspath(f"{i[1]}{i[0]}")
        target = abspath(f"{config['dirOut']}/{i[0]}")
        # print(f"Local: {local} Target: {target}")
        if os.path.exists(local):
            if local != target:
                if os.path.exists(target):
                    print(f"{i[0]} Already installed, skipping...")
                    copyLoop = False
                else:
                    if (not cautiousMode) or getbool("Installing"):
                        os.link(local, target)
        else:
            raise FileNotFoundError(
                f"{i[0]} not found in expected location ({local}). It needs to be copied to {target}."
            )
        del local
        del target
else:
    print("Files already present, skipping...")


needDlAo3Css = False
missing = [
    "01-core.css",
    "02-elements.css",
    "03-region-header.css",
    "04-region-dashboard.css",
    "05-region-main.css",
    "06-region-footer.css",
    "07-interactions.css",
    "08-actions.css",
    "09-roles-states.css",
    "10-types-groups.css",
    "11-group-listbox.css",
    "12-group-meta.css",
    "13-group-blurb.css",
    "14-group-preface.css",
    "15-group-comments.css",
    "16-zone-system.css",
    "17-zone-home.css",
    "18-zone-searchbrowse.css",
    "19-zone-tags.css",
    "20-zone-translation.css",
    "21-userstuff.css",
    "22-system-messages.css",
    "25-media-midsize.css",
    "26-media-narrow.css",
    "27-media-aural.css",
    "28-media-print.css",
]
for filename in os.listdir(os.path.join(config["dirOut"], "ao3css")):
    if (filename in missing) and (
        os.path.getsize(os.path.join(config["dirOut"], "ao3css", filename))
    ):
        missing.remove(filename)
if len(missing) != 0:
    needDlAo3Css = True
else:
    print("AO3 official site-wide CSS already downloaded, skipping...")

if needDlAo3Css:
    doAO3CSSLoop = True
    while doAO3CSSLoop:
        doAO3CSS = getbool(
            "Will now download AO3 CSS files, enter Yes to continue or No to stop."
        )
        if doAO3CSS:
            doAO3CSSLoop = False
        else:
            raise Exception("Operation canceled by user.")

    urlRoot = "https://raw.githubusercontent.com/otwcode/otwarchive/refs/heads/master/public/stylesheets/site/2.0/"
    for sheet in missing:
        url = f"{urlRoot}{sheet[1]}"
        subprocess.run(
            [
                "wget",
                "-O",
                os.path.join(config["dirOut"], "ao3css", sheet),
                url,
            ]
        )


if needCopyFiles or needDlAo3Css:
    print("AO3-DL successfully installed.")
else:
    print("AO3-DL was already installed.")
