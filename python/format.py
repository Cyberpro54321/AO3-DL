#!/usr/bin/env python3

import datetime
import logging
import os.path

import AO3
import bs4

import constants
import network
import raws


def init(
    work: AO3.works.Work,
    dirAO3CSS: str = "ao3css",
    stylesheetsMerged: bool = True,
    dirWorkskins: str = "Workskins",
):
    soup = bs4.BeautifulSoup()
    head = soup.append(soup.new_tag("html")).append(soup.new_tag("head"))
    head.append(soup.new_tag("meta", charset="utf-8"))
    head.append(soup.new_tag("title")).string = work.title

    if stylesheetsMerged:
        stylesheetsList = [
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
    else:
        stylesheetsList = [
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

    for i in stylesheetsList:
        head.append(
            soup.new_tag(
                "link",
                rel="stylesheet",
                type="text/css",
                media=i[0],
                href=f"../{dirAO3CSS}/{i[1]}",
            )
        )
    head.append(
        soup.new_tag("link", rel="stylesheet", href=f"../{dirAO3CSS}/sandbox.css")
    )
    head.append(
        soup.new_tag(
            "link",
            rel="stylesheet",
            href=f"../{dirWorkskins}/{raws.getPrefferedFilenameFromWorkID(id=work.id, extension='.css')}",
        )
    )

    soup.html.append(soup.new_tag("body")).append(
        soup.new_tag("div", id="outer", attrs={"class": "wrapper"})
    ).append(soup.new_tag("div", id="inner", attrs={"class": "wrapper"})).append(
        soup.new_tag(
            "div", id="main", role="main", attrs={"class": "works-show region"}
        )
    )

    preface = soup.find(id="main").append(
        soup.new_tag(
            "div", style="text-align:center;border: 1px dashed black", id="ogLink"
        )
    )
    preface.append(soup.new_tag("h3")).string = work.title
    preface.append(soup.new_tag("p")).string = "Downloaded from the "
    preface.p.append(soup.new_tag("a", href="https://archiveofourown.org/")).string = (
        "Archive Of Our Own"
    )
    preface.p.append(" at ")
    preface.p.append(
        soup.new_tag("a", href=f"https://archiveofourown.org/works/{work.id}/")
    ).string = f"https://archiveofourown.org/works/{work.id}/"
    soup.find(id="main").append(
        soup.new_tag("div", id="ao3Meta", attrs={"class": "wrapper"})
    )
    soup.find(id="main").append(soup.new_tag("div", id="workskin"))
    foreword = soup.new_tag("div", attrs={"class": "preface group"})
    foreword.append(soup.new_tag("h2", attrs={"class": "title heading"}))
    foreword.h2.string = work.title
    foreword.append(soup.new_tag("h3", attrs={"class": "byline heading"}))
    for i in work.authors:
        j = soup.new_tag("a", rel="author", href=i.url)
        foreword.h3.append(j)
        j.string = i.username
        del j
        if i != work.authors[-1]:
            foreword.h3.append(",")
    soup.find(id="workskin").append(foreword)

    soup.find(id="workskin").append(soup.new_tag("div", id="chapters", role="article"))
    return soup


def userstuff_preface(
    soup: bs4.BeautifulSoup,
    work: AO3.works.Work,
    rawSoup: str,
    logger: logging.Logger,
):
    ao3MetaRaw = rawSoup.find("dl", class_="tags")
    ao3MetaRaw["class"] = "work meta group"
    soup.find(id="ao3Meta").append(ao3MetaRaw)
    forewordBlockquotes = rawSoup.find("div", id="preface").find_all(
        "blockquote", class_="userstuff"
    )
    hasStartNotes = (
        work.start_notes
        and work.start_notes
        != "(See the end of the work for other works inspired by this one.)\n"
        and work.start_notes != "(See the end of the work for notes.)\n"
        and len(forewordBlockquotes) > 1
    )
    foreword = soup.find(id="workskin").div

    if work.summary and hasStartNotes:
        workSummaryModuleBQ = forewordBlockquotes[0]
        workStartNotesBQ = forewordBlockquotes[1]
    elif work.summary and not hasStartNotes:
        workSummaryModuleBQ = forewordBlockquotes[0]
    elif hasStartNotes and not work.summary:
        workStartNotesBQ = forewordBlockquotes[0]

    if work.summary:
        workSummaryModule = soup.new_tag("div", attrs={"class": "summary module"})
        workSummaryModule.append(soup.new_tag("h3", attrs={"class": "heading"}))
        workSummaryModule.h3.string = "Summary:"
        workSummaryModule.append(workSummaryModuleBQ)
        foreword.append(workSummaryModule)

    if hasStartNotes:
        workStartNotesModule = soup.new_tag("div", attrs={"class": "notes module"})
        workStartNotesModule.append(soup.new_tag("h3", attrs={"class": "heading"}))
        workStartNotesModule.h3.string = "Notes:"
        workStartNotesModule.append(workStartNotesBQ)
        foreword.append(workStartNotesModule)

    if work.end_notes:
        pass
        afterword = soup.new_tag("div", attrs={"class": "afterword preface group"})
        workEndNotesModule = soup.new_tag(
            "div", id="work_endnotes", attrs={"class": "end notes module"}
        )
        workEndNotesModule.append(soup.new_tag("h3", attrs={"class": "heading"}))
        workEndNotesModule.h3.string = "Notes:"
        workEndNotesModule.append(
            rawSoup.find(id="afterword").find("blockquote", class_="userstuff")
        )
        afterword.append(workEndNotesModule)

        soup.find(id="workskin").append(afterword)
    return soup


def userstuff_loop(
    soup: bs4.BeautifulSoup,
    work: AO3.works.Work,
    rawSoup: str,
    logger: logging.Logger,
):
    divChaptersRaw = rawSoup.find(id="chapters")
    for i in divChaptersRaw.contents:
        if str(i.name)[0:4] == "None":
            i.decompose()

    allForewordsNumbered = {}
    allForewords = divChaptersRaw.find_all("div", class_="meta group")
    for j in work.chapters:
        for div in allForewords:
            if (j.title and j.title == div.h2.string.strip()) or (
                div.h2.string == f"Chapter {j.number}"
            ):
                allForewordsNumbered[j.number] = div
                div.h2.string = ""
                break
    del allForewords

    allChaptersNumbered = {}
    if work.oneshot:
        allChaptersNumbered[1] = divChaptersRaw.find("div", class_="userstuff")
    else:
        allChapters = divChaptersRaw.find_all("div", class_="userstuff")
        for i in work.chapters:
            for j in allChapters:
                text = ""
                for k in j.find_all(("p", "center")):
                    text += k.getText().replace("\n", "") + "\n"
                    if isinstance(k.next_sibling, bs4.element.NavigableString):
                        text += str(k.next_sibling)
                if text == i.text:
                    allChaptersNumbered[i.number] = j
                    break
        del allChapters

    for i in work.chapters:
        doChapter(
            soup=soup,
            chapter=i,
            divChapters=soup.find(id="chapters"),
            currentChapterForewordRaw=allForewordsNumbered.get(i.number),
            currentChapterRaw=allChaptersNumbered[i.number],
            divChaptersRaw=divChaptersRaw,
            logger=logger,
        )
    return soup


def doChapter(
    soup: bs4.BeautifulSoup,
    chapter: AO3.Chapter,
    divChapters: bs4.element.Tag,
    currentChapterForewordRaw: bs4.element.Tag,
    currentChapterRaw: bs4.element.Tag,
    divChaptersRaw: bs4.element.Tag,
    logger: logging.Logger,
):
    logger.info(f"{chapter.title}: {chapter.number}")
    currentChapterDiv = divChapters.append(
        soup.new_tag(
            "div", id="chapter-" + str(chapter.number), attrs={"class": "chapter"}
        )
    )

    # foreword
    currentChapterForeword = currentChapterDiv.append(
        soup.new_tag("div", attrs={"class": "chapter preface group"})
    )
    currentChapterForeword.append(
        soup.new_tag("h3", attrs={"class": "title"})
    ).string = ("Chapter " + str(chapter.number) + ": " + chapter.title)

    # summary
    if chapter.summary:
        currentChapterSummary = currentChapterForeword.append(
            soup.new_tag("div", attrs={"class": "summary module"})
        )
        currentChapterSummary.append(
            soup.new_tag("h3", attrs={"class": "heading"})
        ).string = "Summary:"
        currentChapterSummary.append(currentChapterForewordRaw.blockquote)

    # start notes
    if (
        chapter.start_notes
        and chapter.start_notes.strip() != "(See the end of the chapter for  notes.)"
    ):
        currentChapterStartNotes = currentChapterForeword.append(
            soup.new_tag("div", attrs={"class": "notes module"})
        )
        currentChapterStartNotes.append(
            soup.new_tag("h3", attrs={"class": "heading"})
        ).string = "Notes:"
        currentChapterStartNotes.append(currentChapterForewordRaw.blockquote)

    # chapter main text
    currentChapterDiv.append(
        soup.new_tag("div", role="article", attrs={"class": "userstuff module"})
    ).append(currentChapterRaw)

    # chapter afterword
    if chapter.end_notes:
        currentChapterAfterword = currentChapterDiv.append(
            soup.new_tag(
                "div",
                id=f"endnotes{chapter.number}",
                attrs={"class": "chapter preface group"},
            )
        )
        currentChapterAfterword.append(
            soup.new_tag(
                "div",
                id=f"chapter_{chapter.number}_endnotes",
                atttrs={"class": "end notes module"},
            )
        )
        currentChapterAfterword.div.append(
            soup.new_tag("h3", attrs={"class": "heading"})
        ).string = "Notes:"
        currentChapterAfterword.div.append(
            divChaptersRaw.find("div", id=f"endnotes{chapter.number}").blockquote,
        )


def getImages(
    soup: bs4.BeautifulSoup,
    imgDir: str,
    id: int,
    logger: logging.Logger,
):
    filesDownloaded = {}
    for img in soup.findAll("img"):
        if "src" in img.attrs:
            if img.attrs["src"] in filesDownloaded.keys():
                img.attrs["src"] = filesDownloaded[img.attrs["src"]]
            else:
                filename = network.downloadFile(
                    url=img.attrs["src"], dir=f"{imgDir}/{id}", logger=logger
                )
                if filename == img.attrs["src"]:
                    logger.error(
                        f"Failed to download image {filename}, leaving link to externally-hosted version."
                    )
                    relpath = filename
                else:
                    relpath = f"../{imgDir.split('/')[-1]}/{id}/{filename}"
                filesDownloaded[img.attrs["src"]] = relpath
                img.attrs["src"] = relpath
    if len(filesDownloaded) > 1:
        logger.info(f"Finished downloading {len(filesDownloaded)} images for work {id}")
    return soup


def finish(
    soup: bs4.BeautifulSoup,
    work: AO3.works.Work,
    logger: logging.Logger,
):
    soup.append(
        bs4.Comment(
            f"File written with version {constants.version} of AO3-DL (https://codeberg.org/Cyberpro123/AO3-DL)"
        )
    )
    soup.append(
        bs4.Comment(
            f"Date Written: {datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()}"
        )
    )
    soup.append(bs4.Comment(f"Work Name: {work.title}"))
    soup.append(
        bs4.Comment(f"Work ID: {work.id} (https://archiveofourown.org/works/{work.id})")
    )
    soup.append(bs4.Comment(f"Chapters: {work.nchapters}/{work.expected_chapters}"))
    return soup


def main(
    work: AO3.works.Work,
    raw: str,
    logger: logging.Logger,
    config: dict = {},
):
    if not config:
        import settings

        settings.setup()
        settings.parse()
        config = settings.settings
    with open(raw) as rawFile:
        rawSoup = bs4.BeautifulSoup(rawFile, features="lxml")
    os.makedirs(
        name=f"{config['dirOutput']}/{config['dirOutImg']}/{work.id}", exist_ok=True
    )
    return finish(
        soup=getImages(
            soup=userstuff_loop(
                soup=userstuff_preface(
                    soup=init(
                        work=work,
                        dirAO3CSS=config["dirAO3CSS"],
                        stylesheetsMerged=config["ao3cssMerged"],
                        dirWorkskins=config["dirWorkskins"],
                    ),
                    work=work,
                    rawSoup=rawSoup,
                    logger=logger,
                ),
                work=work,
                rawSoup=rawSoup,
                logger=logger,
            ),
            imgDir=f"{config['dirOutput']}/{config['dirOutImg']}",
            id=work.id,
            logger=logger,
        ),
        work=work,
        logger=logger,
    )
