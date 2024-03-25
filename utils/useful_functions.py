import os
import time
from datetime import datetime

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


def execute_function(function_name, S, y):
    """
    Function used to call the methods to execute the tests

    :param function_name: function name to be executed
    :param S: sequence
    :param y: p value
    :return: output of executed test
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
    """
    This function saves the counters values produced in the statistical analysis

    :param c0: counter C0 values
    :param c1: counter C1 values
    :param elapsed_time: time used to execute the test
    :param shuffle_type: type of shuffle used
    :param f: path to csv file
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


def benchmark_timing(tot_time, p):
    """
    This function saves in a txt file the time taken to execute the tests on the shuffled sequences

    :param tot_time: computed total time
    :param p: string, either "parallelizing" or "non-parallelizing"
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
    """
    Function used to detect whether a folder is already present in the project

    :param base_dir: base path to the directory
    :param current_run_date: date at which the script is run
    :return: the next iteration number for the folder
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
