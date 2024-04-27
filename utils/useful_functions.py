import os
import time
from datetime import datetime

import numpy as np
import pandas as pd

import permutation_tests
import utils.config


def save_counters(
    conf: utils.config.Config, c0: list[int], c1: list[int], elapsed_time: float, shuffle_type: str, f: str
):
    """Saves counters values obtained in the statistical analysis

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    c0 : list of int
        counter C0
    c1 : list of int
        counter C1
    elapsed_time : float
        time to execute a test
    shuffle_type : str
        type of shuffle selected
    f : str
        path to csv file
    """
    header = [
        "n_iterations_c",
        "n_symbols",
        "n_sequences",
        "shuffle",
        "test",
        "COUNTER_0",
        "COUNTER_1",
        "PROCESS_TIME",
        "DATE",
    ]
    elapsed = time.strftime("%H:%M:%S.{}".format(str(elapsed_time % 1)[2:])[:11], time.gmtime(elapsed_time))
    data = [
        conf.stat.n_iterations_c,
        conf.stat.n_symbols,
        conf.stat.n_sequences,
        shuffle_type,
        permutation_tests.tests[conf.stat.distribution_test_index].name,
        c0,
        c1,
        str(elapsed),
        str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
    ]

    # Convert the dictionary to a DataFrame and export it to a csv file
    df = pd.DataFrame(data, index=header).T

    directory = os.path.dirname(f)
    if not os.path.exists(directory):
        os.makedirs(directory)
    h = not os.path.exists(f)

    df.to_csv(f, mode="a", header=h, index=False)


def save_IID_validation(conf: utils.config.Config, C0: list[int], C1: list[int], b: bool, test_time: float):
    """Saves IID failure and the counters values generated in the NIST test part

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    C0 : list of int
        counter C0
    C1 : list of int
        counter C1
    b : bool
        IID assumption
    test_time : float
        total process time
    """
    header = ["n_symbols", "n_sequences", "test_list", "COUNTER_0", "COUNTER_1", "IID", "process_time", "date"]
    d = [
        conf.nist.n_symbols,
        conf.nist.n_sequences,
        [permutation_tests.tests[i].name for i in conf.nist.selected_tests],
        C0,
        C1,
        b,
        test_time,
        str(datetime.now()),
    ]
    dt = pd.DataFrame(d, index=header).T
    h = True
    if os.path.exists("results/IID_validation.csv"):
        h = False
        dt.to_csv("results/IID_validation.csv", mode="a", header=h, index=False)
    else:
        dt.to_csv("results/IID_validation.csv", mode="a", header=h, index=False)


def save_test_values(conf: utils.config.Config, Tx, Ti):
    """Saves Tx test values and Ti test values in a csv file

    Parameters
    ----------
    conf : utils.config.Config
        application configuration parameters
    Tx : list of float
        Tx test values calculated on one sequence
    Ti : list of float
        Ti test values calculated on the shuffled sequences
    """
    if conf.nist.pvalues == conf.nist.DEFAULT_PVALUES:
        header = [
            "excursion_test",
            "n_directional_runs",
            "l_directional_runs",
            "n_median_runs",
            "l_median_runs",
            "n_increases_decreases",
            "avg_collision",
            "max_collision",
            "periodicity_p0",
            "periodicity_p1",
            "periodicity_p2",
            "periodicity_p3",
            "periodicity_p4",
            "covariance_p0",
            "covariance_p1",
            "covariance_p2",
            "covariance_p3",
            "covariance_p4",
            "compression",
        ]
    elif len(conf.nist.pvalues) == 1:
        header = [permutation_tests.tests[i].name for i in conf.nist.selected_tests]
    else:
        raise Exception("Support for arbitrary p values not implemented yet")

    df2 = pd.DataFrame(np.array(Ti), columns=header)
    a = pd.DataFrame([Tx], columns=header)
    df = pd.concat([a, df2]).reset_index(drop=True)
    # df.insert("time Ti", tf, True)
    file_path = "results/save_test_values.csv"
    write_header = not os.path.isfile(file_path)

    # Save the DataFrame to CSV, without the index and with headers only if writing for the first time
    df.to_csv(file_path, mode="a", header=write_header, index=False)


def get_next_run_number(base_dir, current_run_date):
    """Calculates the iteration number to create numbered of sequenced folders


    Parameters
    ----------
    base_dir : str
        base path to the directory
    current_run_date : str
        date at which the script is run

    Returns
    -------
    int
        next iteration number for the folder
    """
    # Check existing directories for the current date
    date_dir = os.path.join(base_dir, current_run_date)
    if not os.path.exists(date_dir):
        os.makedirs(date_dir, exist_ok=True)
        return 1  # If the date directory doesn't exist, start with 1

    existing_runs = os.listdir(date_dir)
    if not existing_runs:
        return 1  # If there are no runs yet for today, start with 1

    # Determine the next run number by finding the maximum existing run number and adding 1
    run_numbers = [int(run) for run in existing_runs if run.isdigit()]
    next_run_number = max(run_numbers) + 1 if run_numbers else 1

    return next_run_number
