import sys

from subtitle_converter import read_input_path

def main(argv):
  if len(argv) != 1:
    raise ValueError("Invalid amount of arguments passed, please pass one (input subtitle directory)")

  return read_input_path(argv[0])

if __name__ == "__main__":
  main(sys.argv[1:])
