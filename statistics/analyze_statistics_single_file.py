import operator
from functools import reduce
from pathlib import Path
from sys import argv
import json


def main(args):
    analyze_statistics_from_file(Path(args[1]))


def analyze_statistics_from_file(stat_file):
    if not stat_file.exists() or not stat_file.is_file():
        print(f'File [{stat_file}] does not exist')
        exit(1)

    data = ""

    try:
        with open(stat_file, "r") as f:
            data = f.read()
    except Exception as err:
        print(err)
        exit(1)

    stat = json.loads(data)
    theories_size = len(stat)

    for i in range(0, theories_size):
        print_logic_statistics((stat["logics"])[i])


def print_logic_statistics(logic):
    tests = logic["TESTS"]
    tests_size = len(tests)

    def passed_tests_func(x): return x["succeeded"]

    def failed_tests_func(x): return not x["succeeded"]

    passed_tests = list(filter(passed_tests_func, tests))
    passed_tests_size = len(passed_tests)
    passed_tests_percent = passed_tests_size / tests_size * 100

    failed_tests = list(filter(failed_tests_func, tests))
    failed_tests_size = len(failed_tests)
    failed_tests_correctness_error = len(
        list(filter(lambda x: failed_tests_func(x) and x["correctness_error"], tests)))
    failed_tests_with_corr_error_size = failed_tests_correctness_error / failed_tests_size * 100

    def elapsed_time_func(x): return x["elapsed_time"]

    elapsed_times = map(elapsed_time_func, tests)
    elapsed_time_sum = reduce(operator.add, elapsed_times)
    avg_elapsed_time = elapsed_time_sum / tests_size

    elapsed_times_passed = map(elapsed_time_func, passed_tests)
    elapsed_time_passed_sum = reduce(operator.add, elapsed_times_passed)
    avg_elapsed_passed_time = elapsed_time_passed_sum / passed_tests_size

    elapsed_times_failed = map(elapsed_time_func, failed_tests)
    elapsed_time_failed_sum = reduce(operator.add, elapsed_times_failed)
    avg_elapsed_failed_time = elapsed_time_failed_sum / failed_tests_size

    def solver_queries_number_func(x): return x["solver_queries_number"]

    solver_queries_numbers = map(solver_queries_number_func, tests)
    solver_queries_numbers_sum = reduce(operator.add, solver_queries_numbers)
    avg_solver_queries_number = solver_queries_numbers_sum / tests_size

    failed_solver_queries_numbers = map(solver_queries_number_func, failed_tests)
    failed_solver_queries_numbers_sum = reduce(operator.add, failed_solver_queries_numbers)
    failed_avg_solver_queries_number = failed_solver_queries_numbers_sum / failed_tests_size

    stat = LogicStatistics(logic["NAME"], logic["TIMEOUT"], tests_size, passed_tests_percent,
                           failed_tests_with_corr_error_size, avg_elapsed_time,
                           avg_elapsed_passed_time, avg_elapsed_failed_time, avg_solver_queries_number,
                           failed_avg_solver_queries_number)

    print(json.dumps(stat.__dict__))

    return stat


class LogicStatistics:
    def __init__(self, logic_name, timeout, tests_size, passed_tests_percent, failed_tests_with_corr_error_size,
                 avg_elapsed_time,
                 avg_elapsed_passed_time, avg_elapsed_failed_time, avg_solver_queries_number,
                 failed_avg_solver_queries_number):
        self.logic_name = logic_name
        self.timeout = timeout
        self.tests_size = tests_size
        self.passed_tests_percent = passed_tests_percent
        self.failed_tests_with_corr_error_size = failed_tests_with_corr_error_size
        self.avg_elapsed_time = avg_elapsed_time
        self.avg_elapsed_passed_time = avg_elapsed_passed_time
        self.avg_elapsed_failed_time = avg_elapsed_failed_time
        self.avg_solver_queries_number = avg_solver_queries_number
        self.failed_avg_solver_queries_number = failed_avg_solver_queries_number


if __name__ == "__main__":
    main(argv)
