import shutil
from os import path, walk, makedirs, remove
from pathlib import Path
from sys import argv


def main(args):
    copy_and_remove_tests_without_answer(Path(args[1]), Path(args[2]))


def copy_and_remove_tests_without_answer(dir_from, dir_to):
    for root, _, files in walk(dir_from):
        for file in files:
            complete_path = path.join(root, file)

            filename, extension = path.splitext(complete_path)
            if extension != ".maxsmt":
                continue

            try:
                test_was_generated = False

                try:
                    with open(complete_path, "r") as f:
                        while True:
                            line = f.readline()

                            if not line:
                                break

                            if "sat_soft_constraints_weights_sum:" in line:
                                test_was_generated = True
                                break
                except Exception as err:
                    print(err)
                    exit(1)

                if test_was_generated:
                    continue

                from_rel_path = str(complete_path).replace(str(dir_from) + "\\", "")
                dst = path.join(dir_to, from_rel_path)
                dst_folder = path.dirname(dst)

                if not path.exists(dst_folder):
                    makedirs(dst_folder)

                if not path.exists(dst):
                    # Copying maxsmt file
                    shutil.copy(complete_path, dst)
                    print("File [" + str(dst) + "] copied")

                    # Remove maxsmt file
                    remove(complete_path)
                    print("File [" + str(complete_path) + "] removed")

                    # Copying smt2 file
                    smt2_filepath = complete_path.replace("maxsmt", "smt2")
                    shutil.copy(smt2_filepath, dst.replace("maxsmt", "smt2"))
                    print("File [" + str(dst.replace("maxsmt", "smt2")) + "] copied")

                    # Remove smt2 file
                    remove(smt2_filepath)
                    print("File [" + str(smt2_filepath) + "] removed")
            except Exception as err:
                print(err)
                exit(1)


if __name__ == "__main__":
    main(argv)
