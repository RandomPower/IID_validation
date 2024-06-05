import logging
import pathlib
import time

from tqdm import tqdm

from . import config, permutation_tests, plot, read, save

# Configure per-module logger
logger = logging.getLogger(f"IID_validation.{pathlib.Path(__file__).stem}")


def calculate_counters_TjNorm(conf: config.Config, S: list[int], Ti: list[list[float]]) -> tuple[list[int], list[int]]:
    """Compute the counters C0 and C1 for a given reference list of values Ti with the TjNorm method.
    The elements of Ti are considered in non-overlapping pairs: the couples with the same Ti values are discarded and
    replaced, then if the first element of the pair is bigger that the following one, C0 is incremented; if they are
    equal C1 is.

    Parameters
    ----------
    conf : config.Config
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


def statistical_analysis_function(conf: config.Config) -> None:
    """Performs the statistical analysis procedure.

    Parameters
    ----------
    conf : config.Config
        application configuration parameters
    """
    stat_tests_names = [permutation_tests.tests[t].name for t in conf.stat.selected_tests]
    logger.debug("STATISTICAL ANALYSIS FOR TESTS %s", stat_tests_names)
    S = read.read_file(conf.input_file, conf.stat.n_symbols)
    logger.debug("Read a sequence of %s symbols from file (%s) ", conf.stat.n_symbols, conf.input_file)

    logger.debug("Calculating the selected test reference statistics (Tx) on the input sequence")
    Tx = permutation_tests.run_tests(S, [conf.stat.p], conf.stat.selected_tests)
    logger.debug("Reference statistics calculated!")

    logger.debug("Building the counter's population")
    counters_C0_Tx = [[]] * conf.stat.n_iterations
    counters_C0_TjNorm = [[]] * conf.stat.n_iterations
    for i in tqdm(range(conf.stat.n_iterations), desc="Running statistical analysis", position=0):
        # Calculate counters for Tx and TjNorm methods
        t0 = time.process_time()
        Ti = permutation_tests.run_tests_permutations(
            S,
            conf.stat.n_permutations,
            conf.stat.selected_tests,
            [conf.stat.p],
            conf.parallel,
            standalone_progress=False,
        )
        t1 = time.process_time()
        C0_Tx, C1_Tx = permutation_tests.calculate_counters(Tx, Ti)
        t2 = time.process_time()
        C0_TjNorm, C1_TjNorm = calculate_counters_TjNorm(conf, S, Ti)
        t3 = time.process_time()
        IID_assumption_Tx = permutation_tests.iid_result(C0_Tx, C1_Tx, conf.stat.n_permutations)
        IID_assumption_TjNorm = permutation_tests.iid_result(C0_TjNorm, C1_TjNorm, int(conf.stat.n_permutations / 2))
        # Save the values of the counters
        save.save_counters(
            conf.stat.n_symbols,
            conf.stat.n_permutations,
            conf.stat.selected_tests,
            C0_Tx,
            C1_Tx,
            IID_assumption_Tx,
            t2 - t0,
            "countersTx_distribution",
        )
        save.save_counters(
            conf.stat.n_symbols,
            conf.stat.n_permutations,
            conf.stat.selected_tests,
            C0_TjNorm,
            C1_TjNorm,
            IID_assumption_TjNorm,
            t3 - t2 + t1 - t0,
            "countersTj_distribution",
        )

        counters_C0_Tx[i] = C0_Tx
        counters_C0_TjNorm[i] = C0_TjNorm

    logger.info("Counters population built!")

    # Plot the distributions of the counters
    for t in range(len(conf.stat.selected_tests)):
        plot.counters_distribution(
            [i[t] for i in counters_C0_Tx],
            conf.stat.n_permutations,
            conf.stat.n_iterations,
            conf.stat.selected_tests[t],
            "Tx",
        )
        plot.counters_distribution(
            [i[t] for i in counters_C0_TjNorm],
            conf.stat.n_permutations,
            conf.stat.n_iterations,
            conf.stat.selected_tests[t],
            "Tj",
        )

    logger.debug("Statistical analysis completed")
