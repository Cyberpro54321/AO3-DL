# AO3-DL
This project is a set of Python scripts (plus PHP scripts and Docker Compose files) meant to automate the proccess of downloading works from [AO3](https://archiveofourown.org) and displaying them in as close to their original forms as possible.

## Warning
This project isn't in a stable state, and I can't gaurentee that the version you download today and the version you may download next week will work the same way or that files produced by one will work with the other.
If you do choose to use this project in its current state please be sure to contact me with any errors you encounter, any questions you have, and any ideas for additions or improvements you have.

## Usage
### Single
To download a singular work, for example `https://archiveofourown.org/works/27665101`, use `main.py`. You can use a link to the work:
```bash
./main.py https://archiveofourown.org/works/27665101
```
or just the Work ID:
```bash
./main.py 27665101
```

### Bulk
To download a large number of works at once, use `bulk.py`, such as:
```bash
./bulk.py batch.txt
```
where `batch.txt` looks something like:
```
27665101
35583634
19055431
```
or
```
https://archiveofourown.org/works/27665101
https://archiveofourown.org/works/35583634
https://archiveofourown.org/works/19055431
```

### Series
`bulk.py` also supports downloading all the works in a particular series. So the following two batch files, for example, are effectively the same:
```
https://archiveofourown.org/series/2429515
```
```
https://archiveofourown.org/works/27665101
https://archiveofourown.org/works/32778985
https://archiveofourown.org/works/37130362
https://archiveofourown.org/works/49109950
```

### Check For Updates
For various reasons, every work you download with `main.py` or `bulk.py` is saved to a database (`main.sqlite` by default).
When you call `bulk.py` without specifying a batch file, it will go through every work saved in the database and re-download any works that've been updated since the last download.
```bash
./bulk.py
```

## Contact
Main source code repository and issue tracker at [Codeberg](https://codeberg.org/Cyberpro123/AO3-DL), mirror also available on [Github](https://github.com/Cyberpro54321/AO3-DL).

## Compatibility & Requirements
AO3-DL is currently developed and tested only on Linux. It may be able to work on MacOS or other UNIX-like operating systems, but I haven't tested this.
`bulk.py` and the image-downloading code use the [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html) module from the Python Standard Library, which is explicitly marked as not being available on Windows, so running `bulk.py` or having image downloading enabled will almost definitely not work right when run with Python For Windows. If you want to try running AO3-DL on a Windows machine anyways, try looking into Docker For Windows.

This project is developed and tested using:
- Python version 3.11.2
- [ao3_api](https://github.com/wendytg/ao3_api) version 2.3.1
- `BeautifulSoup4` version 4.13.3
- `lxml` version 5.4.0
- `requests` version 2.28.1
- (Optional) `git` version 2.48
Earlier or later versions of these projects may work, but I haven't done any testing to see what is the earliest version of each that will work.

## Setup
1. Download the project, either by downloading and extracting a `.zip` file or by running `git clone https://codeberg.org/Cyberpro123/AO3-DL.git` in your terminal / command line.
2. (Optional) Change the settings in [config.ini](python/config.ini) to your liking.
3. Copy [works.php](docker/works.php), [works.css](docker/works.css), [works-inner.php](docker/works-inner.php), and [config.ini](python/config.ini) to the directory your output files will be stored in - with the default settings in `config.ini` this will be `~/Documents/AO3-DL/Output/`. Also copy 
- The contents of the `python` directory are 'portable', meaning they can go in any directory you like so long as they're all in the same directory.
4. Download copies of AO3's official sytlesheets. At the moment this needs to be done manually, will automate soon.
5. (Optional) Launch the web server using `docker compose up -d` in your terminal while in the same directory as [docker-compose.yaml](docker/docker-compose.yaml) and [default.conf](docker/default.conf). You can use any other web server you want if you already have a preference, so long as it supports PHP.
