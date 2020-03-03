SUBTITLE_OUTPUT_FILE_EXTENSIONS = ["idx", "sub"]
SUBTITLE_OUTPUT_EXTENSION = SUBTITLE_OUTPUT_FILE_EXTENSIONS[0]
SUBTITLE_OUTPUT_FORMATS = ["S_VOBSUB", "VobSub"]
SUBTITLE_TRACK_TYPE = "subtitles"
SUBTITLE_TEMP_DIRECTORY = "/tmp/subtitles"

MKV_FILE_EXTENSION = ".mkv"
MKV_MERGED_FILE_SUFFIX = f"-merged{MKV_FILE_EXTENSION}"

BDSup2Sub512_PATH = "/home/pi/Software/BDSup2Sub512.jar"
MKVEXTRACT_PATH = "/usr/bin/mkvextract"

ENCODING = "utf-8"
MAX_CONCURRENCY = 8

ERROR_SIGN = "error"
LOGGER_NAME = "subtitle_converter"

try:
  from own_constants import *
except ModuleNotFoundError:
  pass
