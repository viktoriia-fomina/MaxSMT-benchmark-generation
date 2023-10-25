from pathlib import Path
from sys import argv

from convert_tests_to_weighted_maxsmt import convert_tests_to_weighted_maxsmt
from primary_convert_inc_tests_to_maxsmt import primary_convert_inc_tests_to_maxsmt


def main(args):
    convert_inc_tests_to_maxsmt(Path(args[1]), Path(args[2]))


def convert_inc_tests_to_maxsmt(dir_from, dir_to):
    primary_convert_inc_tests_to_maxsmt(dir_from, dir_to)
    convert_tests_to_weighted_maxsmt(dir_to)


if __name__ == "__main__":
    main(argv)
