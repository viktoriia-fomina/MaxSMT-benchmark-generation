import shutil
from os import path, walk, makedirs
from pathlib import Path
from sys import argv


def main(args):
    copy_unknowns(Path(args[1]), "C:\\Users\\fWX1139906\\github\\INC_UNKNOWN")


def copy_unknowns(dir_from, dir_to):
    for root, _, files in walk(dir_from):
        for file in files:
            complete_path = path.join(root, file)

            try:
                from_rel_path = str(complete_path).replace(str(dir_from) + "\\", "")
                dst = path.join(dir_to, from_rel_path)
                dst_folder = path.dirname(dst)

                met_unknown = False

                try:
                    with open(complete_path, "r") as f:
                        while True:
                            line = f.readline()

                            if not line:
                                break

                            if "(set-info :status unknown)" in line:
                                met_unknown = True
                                break
                except Exception as err:
                    print(err)
                    exit(1)

                if not met_unknown:
                    continue

                if not path.exists(dst_folder):
                    makedirs(dst_folder)

                if not path.exists(dst):
                    shutil.copy(complete_path, dst)
                    print("File [" + str(dst) + "] copied")
            except Exception as err:
                print(err)
                exit(1)


if __name__ == "__main__":
    main(argv)
