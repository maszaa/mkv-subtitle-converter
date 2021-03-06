import hashlib
import os
import subprocess
import sys
import threading
import traceback

from pymkv import MKVFile, MKVTrack

from configuration import *

def remove_subtitle_files(subtitle_files):
  LOGGER.warning("Removing subtitle files")
  for subtitle_file in subtitle_files:
    os.remove(subtitle_file)
    LOGGER.warning(f"Removed subtitle file {subtitle_file}")

    if SUBTITLE_OUTPUT_EXTENSION in subtitle_file:
      sub_subtitle_file = subtitle_file.replace(SUBTITLE_OUTPUT_EXTENSION, SUBTITLE_SUB_OUTPUT_EXTENSION)
      os.remove(sub_subtitle_file)
      LOGGER.warning(f"Removed {SUBTITLE_SUB_OUTPUT_EXTENSION} subtitle file {sub_subtitle_file}")

def convert_subtitle(input_subtitle):
  output_subtitle = f"{input_subtitle}{SUBTITLE_OUTPUT_EXTENSION}"

  LOGGER.info(f"Converting subtitle {input_subtitle}")

  convert = subprocess.run(
    ["java", "-jar", BDSup2Sub512_PATH, "-o", output_subtitle, input_subtitle],
    capture_output=True
  )

  LOGGER.info(convert.args)

  stdout = convert.stdout.decode(sys.stdout.encoding)
  stderr = convert.stderr.decode(sys.stderr.encoding)
  if stdout:
    LOGGER.info(stdout)
  if stderr:
    LOGGER.error(stderr)

  if convert.returncode == 0 and ERROR_SIGN not in stdout.lower():
    LOGGER.info(f"Converted subtitle {input_subtitle} to {output_subtitle}")
    remove_subtitle_files([input_subtitle])

    return output_subtitle

  if ERROR_SIGN in stdout.lower():
    LOGGER.error(stdout)

  msg = f"Conversion failed with code {convert.returncode}, check stdout and stderr"
  LOGGER.error(msg)

def get_subtitle_track_ids(mkv_file):
  subtitle_track_ids = {}

  for track in mkv_file.tracks:
    if track.track_type == SUBTITLE_TRACK_TYPE:
      if track.track_codec not in SUBTITLE_OUTPUT_FORMATS:
        subtitle_track_ids[track.track_id] = track.language
      else:
        LOGGER.info(f"File {mkv_file.title} already has {'/'.join(SUBTITLE_OUTPUT_FORMATS)} subtitles")
        return {}

  return subtitle_track_ids

def get_subtitle_extraction_arguments(filepath_md5, subtitle_track_ids):
  subtitle_arguments = []

  for subtitle_track_id in subtitle_track_ids:
    subtitle_file = os.path.join(SUBTITLE_TEMP_DIRECTORY, f"{filepath_md5}-{subtitle_track_id}")
    subtitle_arguments.append(f"{subtitle_track_id}:{subtitle_file}")

  return subtitle_arguments

def extract_subtitles(filepath, subtitle_arguments):
  LOGGER.info(f"Extracting subtitles from file {filepath}")
  LOGGER.info(subtitle_arguments)

  extract = subprocess.run(
    [MKVEXTRACT_PATH, filepath, "tracks", *subtitle_arguments],
    capture_output=True
  )

  LOGGER.info(extract.args)

  stdout = extract.stdout.decode(sys.stdout.encoding)
  stderr = extract.stderr.decode(sys.stderr.encoding)
  if stdout:
    LOGGER.info(stdout)
  if stderr:
    LOGGER.error(stderr)

  if extract.returncode == 0:
    LOGGER.info(f"Extracted subtitles from file {filepath}")
    extracted_subtitles = [subtitle_argument.split(":").pop() for subtitle_argument in subtitle_arguments if subtitle_argument]
    LOGGER.info(extracted_subtitles)
    return extracted_subtitles

  msg = f"Extraction failed with code {extract.returncode}, check stdout and stderr"
  LOGGER.error(msg)

  return []

def add_subtitle_tracks_to_mkv_file(mkv_file, subtitles):
  for subtitle in subtitles.keys():
    language = subtitles.get(subtitle)
    subtitle_track = MKVTrack(subtitle, language=language)
    mkv_file.add_track(subtitle_track)
    LOGGER.info(f"Added subtitle {subtitle} with language {language} to mkv file {mkv_file.title}")

def mux_mkv_file_with_subprocess(commands):
  mux = subprocess.run(
    commands,
    capture_output=True
  )

  LOGGER.info(mux.args)

  stdout = mux.stdout.decode(sys.stdout.encoding)
  stderr = mux.stderr.decode(sys.stderr.encoding)
  if stdout:
    LOGGER.info(stdout)
  if stderr:
    LOGGER.error(stderr)

  if mux.returncode == 0:
    LOGGER.info("Muxing successful")
  else:
    LOGGER.error(f"Muxing failed with code {mux.returncode}, check stdout and stderr")

  return mux.returncode

def mux_mkv_file(mkv_file, filepath, use_pymkv_mux=False):
  output_file = filepath.replace(MKV_FILE_EXTENSION, MKV_MERGED_FILE_SUFFIX)
  result = None

  LOGGER.info(f"Muxing mkv file {mkv_file.title} to file {output_file}")

  if use_pymkv_mux is True:
    mkv_file.mux(output_file)
  else:
    result = mux_mkv_file_with_subprocess(mkv_file.command(output_file, subprocess=subprocess))

  LOGGER.info(f"Muxed mkv file {mkv_file.title} to file {output_file}")
  return result

def remove_mkv_file(filepath):
  os.remove(filepath)
  LOGGER.warning(f"Removed mkv file {filepath}")

def create_subtitle_temp_dir():
  if not os.path.exists(SUBTITLE_TEMP_DIRECTORY):
    os.makedirs(SUBTITLE_TEMP_DIRECTORY)

def handle_mkv_file(filepath):
  SEMAPHORE.acquire()

  try:
    mkv_file = MKVFile(file_path=filepath)
    subtitle_track_ids = get_subtitle_track_ids(mkv_file)
    proceeded_to_mux = False

    if len(subtitle_track_ids.keys()):
      LOGGER.info(f"Found suitable subtitles in file {filepath}")

      filepath_md5 = hashlib.md5(filepath.encode(encoding=ENCODING)).hexdigest()
      LOGGER.info(f"MD5 hash of file {filepath}: {filepath_md5}")

      subtitle_arguments = get_subtitle_extraction_arguments(filepath_md5, subtitle_track_ids.keys())
      create_subtitle_temp_dir()
      extracted_subtitles = extract_subtitles(filepath, subtitle_arguments)

      if len(extracted_subtitles):
        converted_subtitles = {}

        for subtitle, language in zip(extracted_subtitles, subtitle_track_ids.values()):
          converted_subtitle = convert_subtitle(subtitle)
          if converted_subtitle:
            converted_subtitles[converted_subtitle] = language

        if len(converted_subtitles.keys()):
          proceeded_to_mux = True

          add_subtitle_tracks_to_mkv_file(mkv_file, converted_subtitles)
          success = mux_mkv_file(mkv_file, filepath)

          remove_subtitle_files(converted_subtitles)

          if success == 0 and MKV_REMOVE_ORIGINAL_FILE is True:
            remove_mkv_file(filepath)

    if proceeded_to_mux is False:
      LOGGER.info(f"No subtitles to convert in file {filepath}")

  except Exception:
    LOGGER.error(f"Error occured when handling file {filepath}:")
    LOGGER.error(traceback.format_exc())

  SEMAPHORE.release()

def read_input_path(input_path, jobs):
  try:
    job_name = handle_mkv_file.__name__

    LOGGER.debug(f"Reading {input_path}")
    dir_content = os.listdir(input_path)

    for f in dir_content:
      full_path = os.path.join(input_path, f)

      if any(exclude_file_pattern in full_path for exclude_file_pattern in EXCLUDE_FILE_PATTERNS):
        LOGGER.info(f"{full_path} is excluded in configuration (exclusions: {EXCLUDE_FILE_PATTERNS}, proceeding to next item")
        continue

      if os.path.isdir(full_path):
        LOGGER.debug(f"Found child directory inside {input_path}, reading it")
        read_input_path(full_path, jobs)
      elif os.path.isfile(full_path) and MKV_FILE_EXTENSION in f:
        if f.replace(MKV_FILE_EXTENSION, MKV_MERGED_FILE_SUFFIX) in dir_content:
          LOGGER.info(f"Merged mkv file for file {full_path} already exists, not converting subtitles")
        elif MKV_MERGED_FILE_SUFFIX in f:
          LOGGER.info(f"Mkv file {full_path} includes MKV_MERGED_FILE_SUFFIX '{MKV_MERGED_FILE_SUFFIX}', not converting subtitles")
        else:
          LOGGER.info(f"Found mkv file {full_path}")
          jobs.append(threading.Thread(name=f"{job_name}-{f}", target=handle_mkv_file, args=(full_path, )))
          LOGGER.info(f"Created {job_name} job for file {full_path}")

  except Exception:
    LOGGER.error(f"Error occured when handling input path {input_path}:")
    LOGGER.error(traceback.format_exc())
    return 1

def handle_jobs(jobs):
  for job in jobs:
    job.start()
    LOGGER.info(f"Started job {job.name}")

  for job in jobs:
    job.join()
    LOGGER.info(f"Job {job.name} ready")
