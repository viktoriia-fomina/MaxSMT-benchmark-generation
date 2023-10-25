from os import error
from pathlib import Path
from sys import argv


def main(args):
    print_files_with_unknown(Path(args[1]))


def print_files_with_unknown(directory):
    if not directory.exists():
        error("Directory [" + directory + "] does not exist")

    for file in Path(directory).glob("**/*.smt2"):
        try:
            with open(file, "r") as f:
                while True:
                    line = f.readline()

                    if not line:
                        break

                    if "(set-info :status unknown)" in line:
                        print(str(file))
                        break
        except Exception as err:
            print(err)
            exit(1)


if __name__ == "__main__":
    main(argv)
