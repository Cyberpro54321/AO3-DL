#!/usr/bin/env python3

import os.path
import subprocess

from constants import stylesheetsListLong
import settings

settings.setup()
settings.parse()
config = settings.settings

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
    f"{config['dirOutput']}/{config['dirOutHtml']}",
    f"{config['dirOutput']}/{config['dirOutImg']}",
    f"{config['dirOutput']}/{config['dirWorkskins']}",
    f"{config['dirOutput']}/{config['dirAO3CSS']}",
    os.path.dirname(config["ao3UsernameFile"]),
    os.path.dirname(config["ao3PasswordFile"]),
):
    os.makedirs(i, exist_ok=True)


copiedFiles = (
    ("config.ini", "./"),
    ("main.css", "../docker/"),
    ("main.php", "../docker/"),
    ("index.html", "../docker/"),
)


needCopyFiles = False
for i in copiedFiles:
    target = abspath(f"{config['dirOutput']}/{i[0]}")
    if not os.path.exists(target):
        needCopyFiles = True
    elif not os.path.getsize(target):
        needCopyFiles = True


if needCopyFiles:
    doCopyLoop = True
    while doCopyLoop:
        doCopy = getbool(
            f"Will now copy the following files to {config['dirOutput']}:\n{[x[0] for x in copiedFiles]}\nEnter Yes to continue or No to stop."
        )
        if doCopy:
            doCopyLoop = False
        else:
            raise Exception("Operation canceled by user.")
    for i in copiedFiles:
        local = abspath(f"{i[1]}{i[0]}")
        target = abspath(f"{config['dirOutput']}/{i[0]}")
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
missing = []
for sheet in stylesheetsListLong:
    missing.append(sheet[1])
for filename in os.listdir(f"{config['dirOutput']}/{config['dirAO3CSS']}"):
    if filename in missing:
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
    for sheet in stylesheetsListLong:
        url = f"{urlRoot}{sheet[1]}"
        subprocess.run(
            [
                "wget",
                "-O",
                f"{config['dirOutput']}/{config['dirAO3CSS']}/{sheet[1]}",
                url,
            ]
        )


if needCopyFiles or needDlAo3Css:
    print("AO3-DL successfully installed.")
else:
    print("AO3-DL was already installed.")
