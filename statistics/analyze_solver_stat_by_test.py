import json
from os import listdir, path
from pathlib import Path
from sys import argv
from typing import List


def main(args):
    # Accepts directory with test reports in JSON format.
    # Aceepts file where to save aggregated statistics.
    analyze_solver_stat_by_test(Path(args[1]), Path(args[2]))


def analyze_solver_stat_by_test(directory, filepath):
    if not directory.exists() or not directory.is_dir():
        raise FileExistsError(f"Dir [{str(directory)}] does not exist")

    stats = load_all_stats_from_directory(directory)
    theory_names, has_many_theories_stat = get_theory_names(stats)
    logic_stat_aggregated: List[LogicStatistics] = []

    for theory_name in theory_names:
        # We go by this statistics file as it has more logic than others.
        all_logics_stat = has_many_theories_stat["logics"]
        logic_stat = next((s for s in all_logics_stat if s["NAME"] == theory_name), None)

        if logic_stat is None:
            raise Exception("Logic stat was None, but it should not")

        single_tests_stat: List[SingleTestStatistics] = []

        for test in logic_stat["TESTS"]:
            test_name = test["name"]

            logic_stats = get_logic_stats_for_theory(theory_name, stats)
            test_stat_by_solvers = get_test_stat_by_solvers(test_name, logic_stats)
            single_tests_stat.append(SingleTestStatistics(test_name, test_stat_by_solvers))

        logic_stat_aggregated.append(LogicStatistics(theory_name, single_tests_stat))

    logics_stat_aggregated = AllLogicsStatistics(logic_stat_aggregated)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(logics_stat_aggregated, f, default=obj_dict, indent=2, separators=(',', ': '))


def obj_dict(obj):
    return obj.__dict__


def get_test_stat_by_solvers(test_name, logic_stats):
    test_stats_by_solver = []

    for logic_stat in logic_stats:
        tests = logic_stat["TESTS"]
        test_stat = next((t for t in tests if t["name"] == test_name), None)
        if test_stat is None:
            raise Exception("Test stat was None, but it should not")

        test_stats_by_solver.append(TestStatisticBySolver(
            test_stat["smtSolver"],
            test_stat["elapsedTimeMs"],
            get_score(test_stat["foundSoFarWeight"], test_stat["optimalWeight"])
        ))

    return test_stats_by_solver


def get_score(found_so_far_weight, optimal_weight):
    if optimal_weight == 0:
        return 1
    return found_so_far_weight / float(optimal_weight)


def get_logic_stats_for_theory(theory_name, stats):
    logic_stats = []

    for stat in stats:
        for logic_stat in stat["logics"]:
            if logic_stat["NAME"] == theory_name:
                logic_stats.append(logic_stat)

    if len(logic_stats) == 0:
        raise Exception(f"No logic statistics were found for theory [{theory_name}]")

    return logic_stats


def get_theory_names(stats):
    def comparator(stat):
        return len(list(stat["logics"]))

    has_many_theories_stat = sorted(stats, key=comparator)[0]
    theory_names = []

    for logic in has_many_theories_stat["logics"]:
        theory_names.append(logic["NAME"])

    if len(theory_names) == 0:
        raise Exception("No theories were found")

    return theory_names, has_many_theories_stat


def load_all_stats_from_directory(directory):
    stats = []
    for filename in listdir(directory):
        if filename.endswith("json") and path.isfile(path.join(directory, filename)):
            with open(path.join(directory, filename), "r", encoding="utf-8") as f:
                stat = json.load(f)
                stats.append(stat)

    if len(stats) == 0:
        raise FileExistsError(f"No JSON files were found in [{str(directory)}]")
    return stats


class TestStatisticBySolver:
    def __init__(self, solver, elapsed_time, score):
        self.solver = solver
        self.elapsed_time = elapsed_time
        self.score = score


class SingleTestStatistics:
    def __init__(self, test_name, test_stat_by_solver_list: List[TestStatisticBySolver]):
        self.test_name = test_name
        self.test_stat_by_solver = test_stat_by_solver_list


class LogicStatistics:
    def __init__(self, logic_name, tests_stat: List[SingleTestStatistics]):
        self.logic_name = logic_name
        self.tests_stat = tests_stat


class AllLogicsStatistics:
    def __init__(self, logic_stats_aggregated: List[LogicStatistics]):
        self.logic_stats = logic_stats_aggregated


if __name__ == "__main__":
    main(argv)
