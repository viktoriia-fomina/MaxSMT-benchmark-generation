import json
import operator
from functools import reduce
from pathlib import Path
from sys import argv


def main(args):
    analyze_maxsmt_statistics(Path(args[1]))


def analyze_maxsmt_statistics(stat_file):
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
        logic_stat = create_logic_statistics((stat["logics"])[i])
        print(json.dumps(logic_stat, default=obj_dict))


def obj_dict(obj):
    return obj.__dict__


def create_tests_size_statistics(tests):
    tests_size = len(tests)
    passed_tests_percent = len(list(filter(lambda x: x["passed"], tests))) / tests_size * 100
    failed_tests_size = len(list(filter(lambda x: not x["passed"], tests)))
    failed_tests_wrong_soft_constr_sum_size = len(list(filter(lambda x: x["checkedSoftConstraintsSumIsWrong"], tests)))

    return TestsSizeStatistics(tests_size, passed_tests_percent, failed_tests_size,
                               failed_tests_wrong_soft_constr_sum_size)


def create_tests_queries_to_solver_statistics(tests):
    tests_size = len(tests)

    def max_smt_stat(test):
        return test["maxSMTCallStatistics"]

    def queries_to_solver_number(test):
        if isinstance(test, int):
            return test
        return max_smt_stat(test)["queriesToSolverNumber"]

    def time_in_solver_queries_ms(test):
        if isinstance(test, int):
            return test
        return max_smt_stat(test)["timeInSolverQueriesMs"]

    def elapsed_time_ms(test):
        return max_smt_stat(test)["elapsedTimeMs"]

    avg_queries_to_solver_number = reduce(lambda x, y: queries_to_solver_number(x) + queries_to_solver_number(y),
                                          tests, 0) / tests_size
    avg_time_per_solver_queries_percent_list = map(lambda x: time_in_solver_queries_ms(x) / elapsed_time_ms(x) * 100,
                                                   tests)
    avg_time_per_solver_queries_percent = reduce(operator.add, avg_time_per_solver_queries_percent_list, 0) / tests_size
    failed_tests = list(filter(lambda x: not x["passed"], tests))

    avg_failed_test_queries_to_solver_number = reduce(
        lambda x, y: queries_to_solver_number(x) + queries_to_solver_number(y), failed_tests, 0) / tests_size

    return TestsQueriesToSolverStatistics(avg_queries_to_solver_number, avg_time_per_solver_queries_percent,
                                          avg_failed_test_queries_to_solver_number)


def create_tests_elapsed_time_statistics(tests):
    tests_size = len(tests)

    def max_smt_stat(test):
        return test["maxSMTCallStatistics"]

    def elapsed_time_ms(test):
        if isinstance(test, int):
            return test
        return max_smt_stat(test)["elapsedTimeMs"]

    avg_elapsed_time_ms = reduce(lambda x, y: elapsed_time_ms(x) + elapsed_time_ms(y), tests, 0) / tests_size

    passed_tests = list(filter(lambda x: x["passed"], tests))
    avg_elapsed_passed_tests_time_ms = reduce(lambda x, y: elapsed_time_ms(x) + elapsed_time_ms(y), passed_tests,
                                              0) / tests_size

    failed_tests = list(filter(lambda x: not x["passed"], tests))
    avg_elapsed_failed_tests_time_ms = reduce(lambda x, y: elapsed_time_ms(x) + elapsed_time_ms(y), failed_tests,
                                              0) / tests_size

    return TestsElapsedTimeStatistics(avg_elapsed_time_ms, avg_elapsed_passed_tests_time_ms,
                                      avg_elapsed_failed_tests_time_ms)


class MaxSMTContext:
    def __int__(self, strategy, prefer_large_weight_constraints_for_cores, minimize_cores, get_multiple_cores):
        self.strategy = strategy
        self.prefer_large_weight_constraints_for_cores = prefer_large_weight_constraints_for_cores
        self.minimize_cores = minimize_cores
        self.get_multiple_cores = get_multiple_cores


class TestsSizeStatistics:
    def __init__(self, tests_size, passed_tests_percent, failed_tests_size, failed_tests_wrong_soft_constr_sum_size):
        self.tests_size = tests_size
        self.passed_tests_percent = passed_tests_percent
        self.failed_tests_size = failed_tests_size
        self.failed_tests_wrong_soft_constr_sum_size = failed_tests_wrong_soft_constr_sum_size


class TestsQueriesToSolverStatistics:
    def __init__(self, avg_queries_to_solver_number, avg_time_per_solver_queries_percent,
                 avg_failed_test_queries_to_solver_number):
        self.avg_queries_to_solver_number = avg_queries_to_solver_number
        self.avg_time_per_solver_queries_percent = avg_time_per_solver_queries_percent
        self.avg_failed_test_queries_to_solver_number = avg_failed_test_queries_to_solver_number


class TestsElapsedTimeStatistics:
    def __init__(self, avg_elapsed_time_ms, avg_elapsed_passed_tests_time_ms, avg_elapsed_failed_tests_time_ms):
        self.avg_elapsed_time_ms = avg_elapsed_time_ms
        self.avg_elapsed_passed_tests_time_ms = avg_elapsed_passed_tests_time_ms
        self.avg_elapsed_failed_tests_time_ms = avg_elapsed_failed_tests_time_ms


class LogicTestsStatistics:
    def __init__(self, name, timeout_ms, max_smt_ctx, tests_size_stat: TestsSizeStatistics,
                 tests_queries_to_solver_stat: TestsQueriesToSolverStatistics,
                 tests_elapsed_time_stat: TestsElapsedTimeStatistics):
        self.name = name
        self.timeout_ms = timeout_ms
        self.max_smt_ctx = max_smt_ctx
        self.tests_size_stat = tests_size_stat
        self.tests_queries_to_solver_stat = tests_queries_to_solver_stat
        self.tests_elapsed_time_stat = tests_elapsed_time_stat


def create_logic_statistics(logic):
    tests = logic["TESTS"]
    first_test = tests[0]
    first_test_max_smt_stat = first_test["maxSMTCallStatistics"]
    return LogicTestsStatistics(logic["NAME"], first_test_max_smt_stat["timeoutMs"],
                                first_test_max_smt_stat["maxSmtCtx"], create_tests_size_statistics(tests),
                                create_tests_queries_to_solver_statistics(tests),
                                create_tests_elapsed_time_statistics(tests))


if __name__ == "__main__":
    main(argv)
