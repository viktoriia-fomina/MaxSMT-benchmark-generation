import os
import random
from pathlib import Path
from sys import argv


def main(args):
    create_light_benchmark(Path(args[1]), Path(args[2]), int(args[3]))


def create_light_benchmark(benchmark_dir_from, benchmark_dir_to, tests_num):
    paths = os.listdir(benchmark_dir_from)
    paths.

    for i in range(0, tests_num - 1):
        number = random.randint(0, tests_num - 1)




if __name__ == "__main__":
    main(argv)
