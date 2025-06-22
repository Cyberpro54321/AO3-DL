# Examples
The files in this subdirectory are examples of the sorts of files that can be used with this project's scripts.

## JSON
Files ending in `.json` are whitelist files designed to be passed to [`download.py`](python/download.py) with `./download.py --json <filename.json>` or `./download.py -j <filename.json>`.

### abandoned.json
Blacklists any works with the `Abandoned Work - Unfinished and Discontinued` tag, and any works not marked as complete that haven't been updated[^1] since January 1st 2020.

## Footnotes
[^1]: The "Date Updated" field used here changes when a new chapter is published, not when existing chapters are edited.
