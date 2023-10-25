import random
from enum import Enum
from os import error
from pathlib import Path
from sys import argv


def main(args):
    convert_tests_to_weighted_maxsmt(Path(args[1]))


def convert_tests_to_weighted_maxsmt(directory):
    if not directory.exists():
        error("Directory [" + directory + "] does not exist")

    softs_size = 0

    for file in Path(directory).glob("**/*.maxsmt"):
        try:
            with open(file, "r") as f:
                f.readline()  # We do not need this line
                softs_size = int(f.readline().split(" ")[1])
        except Exception as err:
            print(err)
            exit(1)

        deviation = random.randint(0, 2)

        weights, softs_sum_weight = get_weights(deviation, softs_size)

        try:
            with open(file, "a") as f:
                data = f'soft_constraints_weights: {" ".join(map(str, weights))}\nsoft_constraints_weights_sum: {softs_sum_weight}\n'
                f.write(data)
                print(f"[INFO] {file} maxsmt test information updated: weights added to soft constraints")
        except Exception as err:
            print(err)
            exit(1)


def get_weights(deviation, softs_size):
    max_deviation = get_max_deviation(deviation)
    base_weight = get_base_weight()

    softs_weight = 0

    weights = []

    for i in range(0, softs_size):
        cur_deviation = random.randint(0, max_deviation)
        cur_weight = base_weight + cur_deviation

        softs_weight += cur_weight
        weights.append(cur_weight)

    return weights, softs_weight


def get_max_deviation(deviation):
    if deviation == Deviation.SLIGHT:
        return random.randint(0, 5)
    elif deviation == Deviation.AVERAGE:
        return random.randint(6, 100)
    else:
        return random.randint(101, 1000)


def get_base_weight():
    return random.randint(1, 500)


class Deviation(Enum):
    SLIGHT = 0
    AVERAGE = 1
    BIG = 2


if __name__ == "__main__":
    main(argv)
