# MKV Subtitle Converter

Convert subtitles in MKV file to VobSub and mux them to new MKV file with tracks of the original file

## Requirements

* Java JDK or JRE (tested with openjdk 11.0.6)
* mkvtoolnix (mkvmerge and mkvextract): https://mkvtoolnix.download/ (tested with version v31.0.0)
* BDSup2Sub: https://www.videohelp.com/software/BDSup2Sub (tested with version 5.1.2)
* Python 3.6 or later (tested with 3.7.3)

## Installation

1. Install requirements listed above
2. `git clone https://github.com/maszaa/mkv-subtitle-converter.git`
3. `python3 -m venv <venv-name/path>`
4. `source <venv-name/path>/bin/activate`
5. `cd mkv-subtitle-converter`
6. `pip install -r requirements.txt`

## Configuration

Configuration is at `src/configuration.py`. You can override all variables in `src/local_configuration.py` which is gitignored.

## Usage

(asuming current directory is repository root)

`python src/main.py <mkv-files-source-path>`

The Python script will recursively go through all files and sub directories starting from `<mkv-files-source-path>`.
You can exclude paths and files by providing `EXCLUDE_FILE_PATTERNS` in `src/local_configuration.py`.

For example:

```python
EXCLUDE_FILE_PATTERNS = [
  "Music videos"
]
```

Patterns are case sensitive.
