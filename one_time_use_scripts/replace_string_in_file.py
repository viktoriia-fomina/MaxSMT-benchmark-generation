from pathlib import Path
from sys import argv


def main(args):
    replace_string_in_files(Path(args[1]))


def replace_string_in_files(directory):
    for file in Path(directory).glob("**/*.maxsmt"):
        data = ""

        try:
            with open(file, "rt") as f:
                data = f.read()
        except Exception as err:
            print(err)
            exit(1)

        print(f'[INFO] [{str(file)}] data was read')

        data = data.replace("soft_constraints_sum_weight", "soft_constraints_weights_sum")

        try:
            with open(file, "wt") as f:
                f.write(data)
        except Exception as err:
            print(err)
            exit(1)

        print(f'[INFO] [{str(file)}] data was updated')


if __name__ == "__main__":
    main(argv)
