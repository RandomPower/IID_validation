import logging
import os
import pathlib
import time

import numpy as np

from . import config, permutation_tests, plot, read, save

# Configure per-module logger
logger = logging.getLogger(f"IID_validation.{pathlib.Path(__file__).stem}")


def iid_plots(conf: config.Config, Tx: list[float], Ti: list[list[float]]) -> None:
    """Plots a histogram of Ti values with respect to the Tx test value.

    Parameters
    ----------
    conf : config.Config
        application configuration parameters
    Tx : list of float
        reference test values
    Ti : list of list of float
        test values calculated on shuffled sequences
    """
    histo_dir = "histogram_TxTi"
    # Ensure the directory exists
    os.makedirs(histo_dir, exist_ok=True)

    Ti_transposed = np.transpose(Ti)
    test_names = save.TestResults.test_labels(conf.nist.selected_tests, conf.nist.p)
    test_types = save.TestResults.test_isint(conf.nist.selected_tests, conf.nist.p)
    for t in range(len(Tx)):
        plot.histogram_TxTi(Tx[t], Ti_transposed[t], test_names[t], test_types[t], histo_dir)


def iid_test_function(conf: config.Config) -> None:
    """Performs the IID validation procedure.

    Parameters
    ----------
    conf : config.Config
        application configuration parameters
    """
    logger.debug("IID validation started")
    S = read.read_file(conf.input_file, conf.nist.n_symbols, first_seq=conf.nist.first_seq)
    logger.debug("Read a sequence of %s symbols from file (%s) ", conf.nist.n_symbols, conf.input_file)

    logger.debug("Calculating the selected test reference statistics (Tx) on the input sequence")
    Tx = permutation_tests.run_tests(S, conf.nist.p, conf.nist.selected_tests)
    logger.debug("Reference statistics calculated!")

    logger.debug(
        "Calculating the selected test statistics (Ti) over %s permutations of the input sequence",
        conf.nist.n_permutations,
    )
    t0 = time.process_time()
    Ti = permutation_tests.run_tests_permutations(
        S, conf.nist.n_permutations, conf.nist.selected_tests, conf.nist.p, conf.parallel
    )
    ti = time.process_time() - t0
    logger.debug("Calculated the test statistic (Ti) on each shuffled sequence!")

    save.TestResults.to_binary_file("test_values.bin", conf.nist.selected_tests, Tx, Ti, conf.nist.p)

    logger.debug("Calculating the counters, C0 and C1")
    C0, C1 = permutation_tests.calculate_counters(Tx, Ti)
    logger.debug("C0 = %s", C0)
    logger.debug("C1 = %s", C1)

    logger.debug("Validating IID assumption")
    IID_assumption = permutation_tests.iid_result(C0, C1, conf.nist.n_permutations)

    logger.info("IID assumption %s\n", "validated" if IID_assumption else "rejected")
    # save results of the IID validation
    save.save_counters(
        conf.nist.n_symbols,
        conf.nist.n_permutations,
        conf.nist.selected_tests,
        C0,
        C1,
        IID_assumption,
        ti,
    )

    # plots
    if conf.nist.plot:
        logger.debug("Saving the Tx-Ti plots")
        iid_plots(conf, Tx, Ti)
        logger.debug("Tx-Ti plots saved!\n")
