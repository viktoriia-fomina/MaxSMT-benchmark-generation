from pathlib import Path
from sys import argv


def main(args):
    rename_long_files_names(Path(args[1]))


def rename_long_files_names(directory):
    if not Path.is_dir(directory):
        print(f'[{directory}] is not directory')
        exit(1)

    for file in Path(directory).glob("**/*.*"):
        try:
            old_filename = str(file)
            new_filename = old_filename.replace("_sequence_infinite", "")
            new_filename = new_filename.replace("_main.cil.out.c", "")
            new_filename = new_filename.replace(".cil.c", "")
            file.rename(new_filename)
        except Exception as err:
            print(err)
            exit(1)
        print(f"File [{file}] converted")

    # for root, _, files in walk(dir):
    #    for f in files:
    #        complete_path = path.join(root, f)
    #        if "_main0" in complete_path or "_withcheck_stateful.cil.out.c" in complete_path or "_withcheck" in complete_path:
    #            new_complete_path = complete_path.replace("_withcheck_stateful.cil.out.c", "")
    #            new_complete_path = new_complete_path.replace("_main0", "")
    #            new_complete_path = new_complete_path.replace("_withcheck", "")
    #            rename("\\\\?\\" + complete_path, "\\\\?\\" + new_complete_path)


if __name__ == "__main__":
    main(argv)
