import shutil
from os import path, error, walk, remove
from pathlib import Path
from sys import argv


def main(args):
    print_file_names_with_all_sat_constraints(Path(args[1]))


def print_file_names_with_all_sat_constraints(directory):
    if not directory.exists():
        error("Directory [" + directory + "] does not exist")

    for root, _, files in walk(directory):
        for f in files:
            complete_path = path.join(root, f)
            try:
                check_all_file_constraints_sat(Path(complete_path))
            except Exception as err:
                print(err)
                exit(1)


def check_all_file_constraints_sat(file):
    if not file.exists():
        error("File [" + file + "] does not exist")

    met_unsat_in_softs = False
    met_unsat_in_hards = False
    met_unknown = False
    try:
        with open(file, "r") as f:
            cur_met_pushes = 0

            while True:
                line = f.readline()

                if not line:
                    break

                if "(push 1)" in line:
                    cur_met_pushes += 1
                elif "(pop 1)" in line:
                    cur_met_pushes -= 1
                elif cur_met_pushes > 0 and "(set-info :status unsat)" in line:
                    met_unsat_in_softs = True
                    break
                elif "(set-info :status unsat)" in line:
                    met_unsat_in_hards = True
                elif "(set-info :status unknown)" in line:
                    met_unknown = True
    except Exception as err:
        print(err)
        exit(1)

    if met_unknown:
        return

    if met_unsat_in_softs and not met_unsat_in_hards:
        return
    elif not met_unsat_in_softs and not met_unsat_in_hards:  # All constraints are SAT
        if "README.md" in str(file):
            remove(file)
            print("REMOVED: " + Style.MAGENTA + str(file))
            return
        else:
            shutil.copy(file, "C:\\Users\\fWX1139906\\github\\INC_TO_DELETE")
            remove(file)
            print("REMOVED: " + Style.MAGENTA + str(file))
            return

        print("All SAT: " + Style.RED + str(file))
    elif False:  # not met_unsat_in_softs and met_unsat_in_hards:  # Unsat only in hards
        print("Hards unsat: " + Style.BLUE + str(file))
    elif False:  # met_unsat_in_softs and met_unsat_in_hards:  # Unsat in both hards and softs
        print("All unsat: " + Style.YELLOW + str(file))


# Class of different styles
class Style:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


if __name__ == "__main__":
    main(argv)
