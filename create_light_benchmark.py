import os
import random
import shutil
from pathlib import Path
from sys import argv


def main(args):
    create_light_benchmark(Path(args[1]), Path(args[2]), int(args[3]))


def create_light_benchmark(benchmark_dir_from, benchmark_dir_to, tests_num):
    paths = []
    met_paths = []

    for root, _, files in os.walk(benchmark_dir_from):
        for file in files:
            complete_path = os.path.join(root, file)

            filename, extension = os.path.splitext(complete_path)
            if extension != ".smt2":
                continue

            paths.append(complete_path)

    paths_size = len(paths)
    light_benchmark_paths = []

    for i in range(0, tests_num):
        number = random.randint(0, paths_size - 1)
        while number in met_paths:
            number = random.randint(0, paths_size - 1)

        met_paths.append(number)
        path = paths[number]
        print(f'[ADDED to LIGHT BENCH] {path}')
        light_benchmark_paths.append(path)

    copy_paths_to_light_benchmark(benchmark_dir_from, benchmark_dir_to, light_benchmark_paths)


def copy_paths_to_light_benchmark(benchmark_dir_from, benchmark_dir_to, light_benchmark_paths):
    for root, _, files in os.walk(benchmark_dir_from):
        for file in files:
            complete_path = os.path.join(root, file)

            if complete_path not in light_benchmark_paths:
                continue

            try:
                from_rel_path = str(complete_path).replace(str(benchmark_dir_from) + "\\", "")
                dst = os.path.join(benchmark_dir_to, from_rel_path)
                dst_folder = os.path.dirname(dst)

                if not os.path.exists(dst_folder):
                    os.makedirs(dst_folder)

                if not os.path.exists(dst):
                    shutil.copy(complete_path, dst)
                    print("[COPIED] [" + str(dst) + "]")
                    shutil.copy(complete_path.replace("smt2", "maxsmt"), dst.replace("smt2", "maxsmt"))
                    print("[COPIED] [" + str(dst.replace("smt2", "maxsmt")) + "]")
            except Exception as err:
                print(err)
                exit(1)


if __name__ == "__main__":
    main(argv)
