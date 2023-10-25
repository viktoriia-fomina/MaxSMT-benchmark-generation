from pathlib import Path
from sys import argv


def main(args):
    print_all_sat_unsat_soft_constraints_tests(Path(args[1]))


def print_all_sat_unsat_soft_constraints_tests(directory):
    for file in Path(directory).glob("**/*.maxsmt"):
        try:
            with open(file, "r") as f:
                # We do not need next 3 lines
                f.readline()
                f.readline()
                f.readline()

                softs_weights_sum = int(f.readline().split(" ")[1])
                sat_softs_weights_sum = int(f.readline().split(" ")[1])

                if softs_weights_sum == sat_softs_weights_sum:
                    print(f'[all SAT]: {file}')
                elif sat_softs_weights_sum == 0:
                    print(f'[all UNSAT]: {file}')
        except Exception as err:
            print(err)
            exit(1)


if __name__ == "__main__":
    main(argv)
