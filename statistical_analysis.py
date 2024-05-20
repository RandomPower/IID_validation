import logging
import pathlib

import permutation_tests
import utils.config

# Configure per-module logger
logger = logging.getLogger(f"IID_validation.{pathlib.Path(__file__).stem}")


def calculate_counters_TjNorm(
    conf: utils.config.Config, S: list[int], Ti: list[list[float]]
) -> tuple[list[int], list[int]]:
    """Compute the counters C0 and C1 for a given reference list of values Ti with the TjNorm method. The elements of Ti
    are considered in non-overlapping pairs: the couples with the same Ti values are discarded and replaced, then if the
    first element of the pair is bigger that the following one, C0 is incremented; if they are equal C1 is.

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    S : list of int
        sequence of symbols
    Ti : list of list of float
        list of values to compare for each test

    Returns
    -------
    list of int, list of int
        counter 0 and counter 1
    """
    C0 = [0] * len(conf.stat.selected_tests)
    C1 = [0] * len(conf.stat.selected_tests)

    for u in range(len(conf.stat.selected_tests)):
        for z in range(0, len(Ti) - 1, 2):
            while Ti[z][u] == Ti[z + 1][u]:
                s_shuffled = permutation_tests.FY_shuffle(S.copy())
                Ti[z][u] = permutation_tests.run_tests(s_shuffled, [conf.stat.p], [conf.stat.selected_tests[u]])[0]
                s_shuffled = permutation_tests.FY_shuffle(S.copy())
                Ti[z + 1][u] = permutation_tests.run_tests(s_shuffled, [conf.stat.p], [conf.stat.selected_tests[u]])[0]

            if Ti[z][u] > Ti[z + 1][u]:
                C0[u] += 1
            if Ti[z][u] == Ti[z + 1][u]:
                C1[u] += 1

    return C0, C1
