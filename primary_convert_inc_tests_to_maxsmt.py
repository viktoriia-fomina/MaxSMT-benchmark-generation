from os import path, error, walk, makedirs
from pathlib import Path
from sys import argv


def main(args):
    primary_convert_inc_tests_to_maxsmt(Path(args[1]), Path(args[2]))


def primary_convert_inc_tests_to_maxsmt(dir_from, dir_to):
    if not dir_from.exists():
        error("Directory [" + dir_from + "] does not exist")

    maxsmt_state = MaxSMTState()
    assert_state = MetAssertState()
    declare_fun_state = MetDeclareFunState()

    for root, _, files in walk(dir_from):
        for file in files:
            complete_path = path.join(root, file)
            if not complete_path.endswith(".smt2"):
                continue

            from_rel_path = str(complete_path).replace(str(dir_from) + "\\", "")
            dst = path.join(dir_to, from_rel_path)
            dst_folder = path.dirname(dst)

            declared_functions_names = []
            defined_functions_names = []

            try:
                with open(complete_path, "r") as f1:
                    if not path.exists(dst_folder):
                        makedirs(dst_folder)

                    try:
                        with open(dst, "w+") as f2:
                            softs = []
                            maxsmt_state.__init__()
                            assert_state.__init__()
                            declare_fun_state.__init__()

                            while True:
                                line = f1.readline()

                                if not line:
                                    f2.write("".join(softs))
                                    break

                                # Case when processing multi-line soft assert
                                if assert_state.get_met_soft():
                                    brackets = line.count("(") - line.count(")")
                                    assert_state.update_brackets_number(brackets)
                                    softs.append(line)

                                    if assert_state.brackets_are_balanced():
                                        assert_state.set_not_met_assert()
                                # Case when processing multi-line hard assert
                                elif assert_state.get_met_hard():
                                    f2.write(line)
                                    brackets = line.count("(") - line.count(")")
                                    assert_state.update_brackets_number(brackets)

                                    if assert_state.brackets_are_balanced():
                                        assert_state.set_not_met_assert()
                                # Case when processing multi-line declare fun
                                elif declare_fun_state.get_met():
                                    met_name_now = not declare_fun_state.met_name and get_declared_fun_name(
                                        line) is not None

                                    if met_name_now and not declare_fun_state.met_name:
                                        declare_fun_state.set_met_name()
                                        declared_fun_name = get_declared_fun_name(line)
                                        if declared_fun_name not in declared_functions_names:
                                            declared_functions_names.append(declared_fun_name)
                                            f2.write(declare_fun_state.declare_fun_buffer + line)
                                        else:
                                            declare_fun_state.set_met_before(True)

                                    brackets = line.count("(") - line.count(")")
                                    declare_fun_state.update_brackets_number(brackets)

                                    if declare_fun_state.brackets_are_balanced():
                                        if not met_name_now and declare_fun_state.met_name and not declare_fun_state.met_before:
                                            f2.write(line)
                                        declare_fun_state.set_not_met()
                                    else:
                                        if not met_name_now and not declare_fun_state.met_name:
                                            declare_fun_state.append_line_to_buffer(line)
                                        elif not met_name_now and declare_fun_state.met_name and not declare_fun_state.met_before:
                                            f2.write(line)
                                # Case when processing new scope beginning
                                elif "(push 1)" in line:
                                    maxsmt_state.cur_met_pushes += 1
                                # Case when processing new scope ending
                                elif "(pop 1)" in line:
                                    maxsmt_state.cur_met_pushes -= 1
                                # Case when processing new soft assert beginning
                                elif maxsmt_state.cur_met_pushes > 0 and "(assert" in line:
                                    maxsmt_state.softs_size += 1
                                    softs.append(line)

                                    brackets = line.count("(") - line.count(")")
                                    if brackets > 0:
                                        assert_state.set_met_soft(brackets)
                                # Case when processing new hard assert beginning
                                elif "(assert" in line:
                                    f2.write(line)
                                    maxsmt_state.hards_size += 1

                                    brackets = line.count("(") - line.count(")")
                                    if brackets > 0:
                                        assert_state.set_met_hard(brackets)
                                # Case when processing new declare fun beginning
                                elif "(declare-fun" in line:
                                    declared_fun_name = get_declared_fun_name(line)

                                    met_name = declared_fun_name is not None
                                    met_name_before = declared_fun_name in declared_functions_names

                                    if met_name and not met_name_before:
                                        declared_functions_names.append(declared_fun_name)
                                        f2.write(line)

                                    brackets = line.count("(") - line.count(")")

                                    if brackets > 0:
                                        declare_fun_state.set_met(met_name, brackets)

                                        if not met_name:
                                            declare_fun_state.append_line_to_buffer(line)
                                        elif met_name_before:
                                            declare_fun_state.set_met_before(True)
                                elif "(define-fun" in line:
                                    defined_fun_name = get_defined_fun_name(line)

                                    if defined_fun_name not in defined_functions_names:
                                        defined_functions_names.append(defined_fun_name)
                                        f2.write(line)
                                elif "(exit)" not in line and "(check-sat)" not in line and "(set-info :status " not in line:
                                    f2.write(line)

                            f2.write("(exit)")

                            # We are not interested in cases when there are no soft constraints
                            if maxsmt_state.softs_size == 0:
                                maxsmt_state.softs_size = maxsmt_state.hards_size
                                maxsmt_state.hards_size = 0

                            filename = path.splitext(dst)[0]

                            print(f"[INFO] {dst} primary maxsmt test created")

                            try:
                                maxsmt_file = filename + ".maxsmt"
                                with open(maxsmt_file, "w+") as f:
                                    data = f'hard_constraints_size: {maxsmt_state.hards_size}\nsoft_constraints_size: {maxsmt_state.softs_size}\n'
                                    f.write(data)
                                    print(f"[INFO] {maxsmt_file} primary maxsmt test information created")
                            except Exception as err:
                                print(err)
                                exit(1)

                    except Exception as err:
                        print(err)
                        exit(1)
            except Exception as err:
                print(err)
                exit(1)


def get_declared_fun_name(line):
    # Function beginning, first elements as the string starts from '(' character
    new_line = line.split("(")[1]

    # For cases like: (declare-fun |*(struct_gsmi_buf)*@2| () ())
    if new_line.count("|") % 2 != 0:
        new_line = line.split(" ")[1]

    declared_fun_name = None

    if new_line.count("|") > 1:
        split_line = new_line.split("|")
        declared_fun_name = split_line[1]
    # Exclude case when there is no name on the current line
    elif not new_line[len("(declare-fun"):].isspace():
        split_line = new_line.split(" ")
        declared_fun_name = split_line[1]

    return declared_fun_name


def get_defined_fun_name(line):
    new_line = line.replace("(define-fun ", "").strip()

    if new_line[0] == '|':
        split_line = new_line.split('|')
        return split_line[1]
    else:
        return new_line.split(' ')[0]


class MaxSMTState:
    def __init__(self):
        self.reading_soft = False
        self.cur_met_pushes = 0
        self.softs_size: int = 0
        self.hards_size: int = 0


class MetAssertState:
    def __init__(self):
        self.met_assert = False
        self.met_soft_assert = False
        self.non_paired_brackets_in_assert = 0

    def set_not_met_assert(self):
        self.met_assert = False
        self.met_soft_assert = False
        self.non_paired_brackets_in_assert = 0

    def get_met_soft(self):
        return self.met_soft_assert

    def get_met_hard(self):
        return self.met_assert and self.met_soft_assert

    def set_met_soft(self, non_paired_brackets_number):
        self.met_assert = True
        self.met_soft_assert = True
        self.non_paired_brackets_in_assert = non_paired_brackets_number

    def set_met_hard(self, non_paired_brackets_number):
        self.met_assert = True
        self.met_soft_assert = False
        self.non_paired_brackets_in_assert = non_paired_brackets_number

    def update_brackets_number(self, non_paired_brackets_number):
        self.non_paired_brackets_in_assert += non_paired_brackets_number

    def brackets_are_balanced(self):
        return self.non_paired_brackets_in_assert == 0


class MetDeclareFunState:
    def __init__(self):
        self.met_declare_fun = False
        self.met_name = False
        self.met_before = None
        self.non_paired_brackets_in_assert = 0
        self.declare_fun_buffer = ""

    def append_line_to_buffer(self, line):
        self.declare_fun_buffer += line

    def set_not_met(self):
        self.met_declare_fun = False
        self.met_name = False
        self.met_before = False
        self.non_paired_brackets_in_assert = 0
        self.declare_fun_buffer = ""

    def get_met(self):
        return self.met_declare_fun

    def set_met(self, met_name, non_paired_brackets_number):
        self.met_declare_fun = True
        self.met_name = met_name
        self.non_paired_brackets_in_assert = non_paired_brackets_number

    def set_met_name(self):
        self.met_name = True

    def set_met_before(self, met_before):
        self.met_before = met_before

    def update_brackets_number(self, non_paired_brackets_number):
        self.non_paired_brackets_in_assert += non_paired_brackets_number

    def brackets_are_balanced(self):
        return self.non_paired_brackets_in_assert == 0


if __name__ == "__main__":
    main(argv)
