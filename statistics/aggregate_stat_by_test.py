import json
from enum import Enum
from pathlib import Path
from sys import argv


def main(args):
    # Accepts file to analyze.
    # Accepts file where to save aggregated statistics.
    aggregate_stat_by_test(Path(args[1]))


def aggregate_stat_by_test(stat_path_from):
    if not stat_path_from.exists() or not stat_path_from.is_file():
        raise FileExistsError(f"File [{str(stat_path_from)}] does not exist")

    with open(stat_path_from, "r", encoding="utf-8") as f:
        stat = json.load(f)

    stats = stat["logic_stats"]

    # All tests.
    count_all_tests_by_solver = {
        Solver.Z3.name: 0,
        Solver.BITWUZLA.name: 0,
        Solver.YICES.name: 0,
        Solver.CVC5.name: 0,
        Solver.PORTFOLIO.name: 0,
        Solver.Z3_NATIVE.name: 0
    }

    # Passed tests.
    count_passed_tests_by_solver = {
        Solver.Z3.name: 0,
        Solver.BITWUZLA.name: 0,
        Solver.YICES.name: 0,
        Solver.CVC5.name: 0,
        Solver.PORTFOLIO.name: 0,
        Solver.Z3_NATIVE.name: 0
    }

    # Count best passed tests.
    count_tests_solver_best = {
        Solver.Z3.name: 0,
        Solver.BITWUZLA.name: 0,
        Solver.YICES.name: 0,
        Solver.CVC5.name: 0,
        Solver.PORTFOLIO.name: 0,
        Solver.Z3_NATIVE.name: 0
    }

    # Passed means no timeout exceeded or UNKNOWN set to true.
    solver_to_elapsed_time_passed_tests_ms = {
        Solver.Z3.name: 0,
        Solver.BITWUZLA.name: 0,
        Solver.YICES.name: 0,
        Solver.CVC5.name: 0,
        Solver.PORTFOLIO.name: 0,
        Solver.Z3_NATIVE.name: 0
    }

    for logic_stat in stats:
        tests_stat = logic_stat["tests_stat"]
        for test_stat in tests_stat:
            best_solvers = get_best_solvers_for_optimal_test(test_stat)

            if len(best_solvers) == 0:
                print(f"No best solver for test [{test_stat["test_name"]}]")

            for solver in best_solvers:
                count_tests_solver_best[solver] += 1

            solvers_passed_test_number = get_solvers_passed_test_number(test_stat)
            for solver in solvers_passed_test_number:
                count_passed_tests_by_solver[solver] += 1

            solvers_executed_test = get_solvers_executed_test(test_stat)
            for solver in solvers_executed_test:
                count_all_tests_by_solver[solver] += 1

            elapsed_time_passed_test_for_solvers = count_elapsed_time_for_every_solver_passed_test(test_stat)

            for key, value in elapsed_time_passed_test_for_solvers.items():
                solver_to_elapsed_time_passed_tests_ms[key] += value

    print("\nAll tests solver tried to execute")
    print(count_all_tests_by_solver)

    print("\n Passed tests by solver")
    print(count_passed_tests_by_solver)

    print(f"\nZ3 was best on {count_tests_solver_best.get(Solver.Z3.name)} tests")
    print(f"Bitwuzla was best on {count_tests_solver_best.get(Solver.BITWUZLA.name)} tests")
    print(f"Yices was best on {count_tests_solver_best.get(Solver.YICES.name)} tests")
    print(f"CVC5 was best on {count_tests_solver_best.get(Solver.CVC5.name)} tests")
    print(f"Portfolio was best on {count_tests_solver_best.get(Solver.PORTFOLIO.name)} tests")
    print(f"Z3_Native was best on {count_tests_solver_best.get(Solver.Z3_NATIVE.name)} tests\n\n")

    print("Solver to elapsed time (cases where timeout has not been exceeded and without UNKNOWN status)")
    print(solver_to_elapsed_time_passed_tests_ms)


def count_elapsed_time_for_every_solver_passed_test(test):
    test_stat_by_solver = test["test_stat_by_solver"]
    solver_to_elapsed_time_ms = {}

    for solver_stat in test_stat_by_solver:
        solver = solver_stat["solver"]
        elapsed_time = solver_stat["elapsed_time"]
        timeout_exceeded_or_unknown = solver_stat["timeout_exceeded_or_unknown"]

        if not timeout_exceeded_or_unknown:
            solver_to_elapsed_time_ms[solver] = elapsed_time

    return solver_to_elapsed_time_ms


# TODO: also support suboptimal case.
# If all solvers got timeout exceeded or UNKNOWN then we'll return an empty list.
def get_best_solvers_for_optimal_test(test):
    test_stat_by_solver = test["test_stat_by_solver"]

    best_elapsed_time = 999999999999999
    best_solvers = []
    for solver_stat in test_stat_by_solver:
        score = solver_stat["score"]
        solver = solver_stat["solver"]
        elapsed_time = solver_stat["elapsed_time"]
        timeout_exceeded_or_unknown = solver_stat["timeout_exceeded_or_unknown"]

        if not timeout_exceeded_or_unknown and abs(score - 1) < 0.0000000001 and elapsed_time < best_elapsed_time:
            best_solvers = [solver]
            best_elapsed_time = elapsed_time
        elif not timeout_exceeded_or_unknown and abs(score - 1) < 0.0000000001 and elapsed_time == best_elapsed_time:
            best_solvers.append(solver)
    return best_solvers


def get_solvers_executed_test(test):
    test_stat_by_solver = test["test_stat_by_solver"]
    solvers = []

    for solver_stat in test_stat_by_solver:
        solver = solver_stat["solver"]
        solvers.append(solver)

    return solvers


# No timeout exceeded or UNKNOWN.
def get_solvers_passed_test_number(test):
    test_stat_by_solver = test["test_stat_by_solver"]
    solvers = []

    for solver_stat in test_stat_by_solver:
        solver = solver_stat["solver"]
        timeout_exceeded_or_unknown = solver_stat["timeout_exceeded_or_unknown"]

        if not timeout_exceeded_or_unknown:
            solvers.append(solver)

    return solvers


class Solver(Enum):
    Z3 = "Z3"
    BITWUZLA = "BITWUZLA"
    YICES = "YICES"
    CVC5 = "CVC5"
    PORTFOLIO = "PORTFOLIO"
    Z3_NATIVE = "Z3_NATIVE"


if __name__ == "__main__":
    main(argv)
