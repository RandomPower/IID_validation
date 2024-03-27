import os
import time
from datetime import datetime

import numpy as np
import pandas as pd

import tests.collision.avg_collision
import tests.collision.max_collision
import tests.compression
import tests.covariance
import tests.excursion_test
import tests.periodicity
import tests.runs.l_directional_runs
import tests.runs.l_runs_median
import tests.runs.n_increases_decreases
import tests.runs.n_of_directional_runs
import tests.runs.n_runs_median
import utils.config


def s_prime(S):
    """Generates a transformed sequence based on the comparison of consecutive elements in the input sequence.
    For each pair of consecutive elements, if the first element is greater than the second, a -1 
    is appended to the new sequence; otherwise, a +1 is appended

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    list of int
        new sequence of -1s and +1s
    """
    S_prime = []
    L = len(S)
    for i in range(L - 1):
        if S[i] > S[i + 1]:
            S_prime.append(-1)
        else:
            S_prime.append(1)
    return S_prime


def s_prime_median(S):
    """Generates a transformed sequence where each original value is replaced with -1 if it is 
    less than the median of the original sequence, or 1 if it is greater than or equal to the median

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    list of int
        new sequence of -1s and +1s
    """
    M = np.median(S)
    S_prime = []
    L = len(S)
    for i in range(L):
        if S[i] < M:
            S_prime.append(-1)
        else:
            S_prime.append(1)
    return S_prime


def execute_function(function_name, S, y):
    """Calls functions to execute based on the function name provided

    Parameters
    ----------
    function_name : str
        function name to be executed
    S : list of int
        sequence of sample values
    y : int
        lag parameter p

    Returns
    -------
    int or float
        output of the executed test function
    """
    return {
        "excursion_test": lambda: tests.excursion_test.excursion_test(S),
        "n_directional_runs": lambda: tests.runs.n_of_directional_runs.n_directional_runs(S),
        "l_directional_runs": lambda: tests.runs.l_directional_runs.l_directional_runs(S),
        "n_median_runs": lambda: tests.runs.n_runs_median.n_median_runs(S),
        "l_median_runs": lambda: tests.runs.l_runs_median.l_median_runs(S),
        "n_increases_decreases": lambda: tests.runs.n_increases_decreases.n_increases_decreases(S),
        "avg_collision": lambda: tests.collision.avg_collision.avg_c(S),
        "max_collision": lambda: tests.collision.max_collision.max_c(S),
        "periodicity": lambda: tests.periodicity.periodicity(S, y),
        "covariance": lambda: tests.covariance.covariance(S, y),
        "compression": lambda: tests.compression.compression(S),
    }[function_name]()


def save_counters(c0, c1, elapsed_time, shuffle_type, f):
    """Saves counters values obtained in the statistical analysis

    Parameters
    ----------
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
        utils.config.n_iterations_c_stat,
        utils.config.n_symbols_stat,
        utils.config.n_sequences_stat,
        shuffle_type,
        utils.config.test,
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


def save_failure_test(C0, C1, b, test_time):
    """Saves IID failure and the counters values generated in the NIST test part

    Parameters
    ----------
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
    t = [utils.config.test_list.get(i) for i in utils.config.test_list_indexes]
    d = [utils.config.n_symbols, utils.config.n_sequences, t, C0, C1, b, test_time, str(datetime.now())]
    dt = pd.DataFrame(d, index=header).T
    h = True
    if os.path.exists("results/failure_rate.csv"):
        h = False
        dt.to_csv("results/failure_rate.csv", mode="a", header=h, index=False)
    else:
        dt.to_csv("results/failure_rate.csv", mode="a", header=h, index=False)


def save_test_values(Tx, Ti):
    """Saves Tx test values and Ti test values in a csv file

    Parameters
    ----------
    Tx : list of float 
        Tx test values calculated on one sequence
    Ti : list of float
        Ti test values calculated on the shuffled sequences
    """
    if utils.config.bool_pvalue:
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
    else:
        header = [utils.config.test_list[k] for k in utils.config.test_list_indexes]
    df2 = pd.DataFrame(np.array(Ti), columns=header)
    a = pd.DataFrame([Tx], columns=header)
    df = pd.concat([a, df2]).reset_index(drop=True)
    # df.insert("time Ti", tf, True)
    file_path = "results/save_test_values.csv"
    write_header = not os.path.isfile(file_path)
    write_mode = "w" if write_header else "a"

    # Save the DataFrame to CSV, without the index and with headers only if writing for the first time
    df.to_csv(file_path, mode=write_mode, header=write_header, index=False)


def benchmark_timing(tot_time, p):
    """Saves time taken to execute the tests on the shuffled sequences in a txt file 

    Parameters
    ----------
    tot_time : float
        total process time
    p : string
        parallelized / non parallelized mode
    """
    if len(utils.config.test_list_indexes) == 11:
        test_ind = "all tests run"
    else:
        test_ind = "tests run: " + str(utils.config.test_list_indexes)
    lines = [
        str(datetime.now()),
        "n_symbols: " + str(utils.config.n_symbols),
        "n_sequences: " + str(utils.config.n_sequences),
        test_ind,
        "total_time: " + str(tot_time) + " s",
        p,
    ]
    with open("results/benchmark_timing_Ti_NIST_test.txt", "a") as f:
        f.write("\n".join(map(str, lines)) + "\n" "\n")


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
