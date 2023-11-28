from pathlib import Path
from sys import argv


def main(args):
    search_for_substr(Path(args[1]))


def search_for_substr(directory):
    print(f"[INFO] process directory [{str(directory)}]")
    files = []

    for file in Path(directory).glob("**/*.smt2"):
        try:
            with open(file, "r") as f:
                while True:
                    line = f.readline()

                    if not line:
                        break

                    filename = str(file)

                    if "(push" in line:
                        if filename not in files:
                            files.append(filename)
                    #elif "push" in line:
                    #    if filename not in files:
                    #        files.append(filename)
                    elif "(pop" in line:
                        if filename not in files:
                            files.append(filename)
                    #elif "pop" in line:
                    #    if filename not in files:
                    #        files.append(filename)
        except Exception as err:
            print(err)
            exit(1)

    print("\n".join(files))


if __name__ == "__main__":
    main(argv)
