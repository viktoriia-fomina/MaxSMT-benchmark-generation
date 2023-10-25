from os import path, walk, remove, error
from pathlib import Path
from sys import argv


def main(args):
    remove_big_files(Path(args[1]))


def remove_big_files(directory):
    if not directory.exists():
        error("Directory [" + directory + "] does not exist")

    for root, _, files in walk(directory):
        for f in files:
            complete_path = path.join(root, f)
            try:
                # set the size of the files you want to delete
                if path.getsize(complete_path) > 1024 * 1024 * 256:  # 256 megabytes
                    print(complete_path)
                    # function to delete the files
                    remove(complete_path)
            except Exception as err:
                print(err)
                exit(1)


if __name__ == "__main__":
    main(argv)
