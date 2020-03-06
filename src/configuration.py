import logging
import sys
import threading

SUBTITLE_OUTPUT_EXTENSION = ".idx"
SUBTITLE_SUB_OUTPUT_EXTENSION = ".sub"
SUBTITLE_OUTPUT_FORMATS = ["S_VOBSUB", "VobSub"]
SUBTITLE_TRACK_TYPE = "subtitles"
SUBTITLE_TEMP_DIRECTORY = "/tmp/subtitles"

MKV_FILE_EXTENSION = ".mkv"
MKV_MERGED_FILE_SUFFIX = f"-merged{MKV_FILE_EXTENSION}"
MKV_REMOVE_ORIGINAL_FILE = False

EXCLUDE_FILE_PATTERNS = []

BDSup2Sub512_PATH = "/home/pi/Software/BDSup2Sub512.jar"
MKVEXTRACT_PATH = "/usr/bin/mkvextract"

ENCODING = "utf-8"
MAX_CONCURRENCY = 4

SEMAPHORE = threading.Semaphore(value=MAX_CONCURRENCY)

ERROR_SIGN = "error"

LOGGER_NAME = "subtitle_converter"
LOG_FORMAT = "[%(asctime)-15s: %(levelname)s/%(funcName)s] %(message)s"
LOG_FORMATTER = logging.Formatter(LOG_FORMAT)

LOGGER = logging.getLogger(LOGGER_NAME)
LOGGER.setLevel(logging.DEBUG)

STDOUT_HANDLER = logging.StreamHandler(sys.stdout)
STDOUT_HANDLER.setFormatter(LOG_FORMATTER)
LOGGER.addHandler(STDOUT_HANDLER)

STDERR_HANDLER = logging.StreamHandler(sys.stderr)
STDERR_HANDLER.setFormatter(LOG_FORMATTER)
STDERR_HANDLER.setLevel(logging.ERROR)
LOGGER.addHandler(STDERR_HANDLER)

try:
  from local_configuration import *
except ModuleNotFoundError:
  pass
