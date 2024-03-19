import numpy as np
import pandas as pd
import os
import time
from datetime import datetime
from architecture.utils.config import n_symbols, n_sequences, n_symbols_stat, n_iterations_c_stat, test, \
    n_sequences_stat, test_list_indexes, \
    test_list, bool_pvalue, bool_shuffle_stat
from architecture.tests.periodicity import periodicity
from architecture.tests.excursion_test import excursion_test
from architecture.tests.runs.n_of_directional_runs import n_directional_runs
from architecture.tests.runs.l_directional_runs import l_directional_runs
from architecture.tests.runs.n_runs_median import n_median_runs
from architecture.tests.runs.l_runs_median import l_median_runs
from architecture.tests.runs.n_increases_decreases import n_increases_decreases
from architecture.tests.collision.avg_collision import avg_c
from architecture.tests.collision.max_collision import max_c
from architecture.tests.covariance import covariace
from architecture.tests.compression import compression


def s_prime(S):
    S_prime = []
    L = len(S)
    for i in range(L - 1):
        if S[i] > S[i + 1]:
            S_prime.append(-1)
        else:
            S_prime.append(1)
    return S_prime


def s_prime_median(S):
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
    """
    Function used to call the methods to execute the tsts

    :param function_name: function name to be executed
    :param S: sequence
    :param y: p value
    :return: output of executed test
    """
    return {
        'excursion_test': lambda: excursion_test(S),
        'n_directional_runs': lambda: n_directional_runs(S),
        'l_directional_runs': lambda: l_directional_runs(S),
        'n_median_runs': lambda: n_median_runs(S),
        'l_median_runs': lambda: l_median_runs(S),
        'n_increases_decreases': lambda: n_increases_decreases(S),
        'avg_collision': lambda: avg_c(S),
        'max_collision': lambda: max_c(S),
        'periodicity': lambda: periodicity(S, y),
        'covariance': lambda: covariace(S, y),
        'compression': lambda: compression(S)
    }[function_name]()


def save_counters(c0, c1, elapsed_time, type, f):
    """
    This function saves the counters values produced in the statistical analysis

    :param c0: counter C0 values
    :param c1: counter C1 values
    :param elapsed_time: time used to execute the test
    :param type: type of shuffle used
    :param f: path to csv file
    """
    header = ['n_iterations_c', 'n_symbols', 'n_sequences', 'shuffle', 'test', 'COUNTER_0',
              'COUNTER_1',
              'PROCESS_TIME', 'DATE']
    elapsed = time.strftime("%H:%M:%S.{}".format(str(elapsed_time % 1)[2:])[:11], time.gmtime(elapsed_time))
    data = [n_iterations_c_stat, n_symbols_stat, n_sequences_stat, type, test, c0, c1, str(elapsed),
            str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))]

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(data, index=header).T

    # Crea la directory se non esiste
    directory = os.path.dirname(f)
    if not os.path.exists(directory):
        os.makedirs(directory)

    h = not os.path.exists(f)
    # Esporta il DataFrame in un file CSV
    df.to_csv(f, mode='a', header=h, index=False)


def save_failure_test(C0, C1, b, test_time):
    """
    This function IID failure and the counters values executed in the NIST test part

    :param c0: counter C0 values
    :param c1: counter C1 values
    :param b: bool IID (True of False)
    :param test_time: time taken for the execution
    """
    header = ['n_symbols', 'n_sequences', 'test_list', 'COUNTER_0', 'COUNTER_1', 'IID', 'process_time', 'date']
    t = [test_list.get(i) for i in test_list_indexes]
    d = [n_symbols, n_sequences, t, C0, C1, b, test_time, str(datetime.now())]
    dt = pd.DataFrame(d, index=header).T
    h = True
    if os.path.exists('results/failure_rate.csv'):
        h = False
        dt.to_csv('results/failure_rate.csv', mode='a', header=h, index=False)
    else:
        dt.to_csv('results/failure_rate.csv', mode='a', header=h, index=False)


def save_test_values(Tx, Ti):
    """
    This function saves the Tx reference values and the Ti values in csv file

    :param Tx: Tx vector with reference values
    :param Ti: Ti vector with test values
    """
    if bool_pvalue:
        header = ['excursion_test', 'n_directional_runs', 'l_directional_runs', 'n_median_runs', 'l_median_runs',
                  'n_increases_decreases', 'avg_collision', 'max_collision', 'periodicity_p0', 'periodicity_p1',
                  'periodicity_p2', 'periodicity_p3', 'periodicity_p4', 'covariance_p0', 'covariance_p1',
                  'covariance_p2', 'covariance_p3', 'covariance_p4', 'compression']
    else:
        header = [test_list[k] for k in test_list_indexes]
    df2 = pd.DataFrame(np.array(Ti), columns=header)
    a = pd.DataFrame([Tx], columns=header)
    df = pd.concat([a, df2]).reset_index(drop=True)
    # df.insert("time Ti", tf, True)
    file_path = 'results/save_test_values.csv'
    write_header = not os.path.isfile(file_path)
    write_mode = 'w' if write_header else 'a'

    # Save the DataFrame to CSV, without the index and with headers only if writing for the first time
    df.to_csv(file_path, mode=write_mode, header=write_header, index=False)


def benchmark_timing(tot_time, p):
    """
    This function saves in a txt file the time taken to execute the tests on the shuffled sequences

    :param tot_time: computed total time
    """
    if len(test_list_indexes) == 11:
        test_ind = "all tests run"
    else:
        test_ind = "tests run: " + str(test_list_indexes)
    lines = [str(datetime.now()), "n_symbols: " + str(n_symbols), "n_sequences: " + str(n_sequences), test_ind,
             "total_time: " + str(tot_time) + " s", p]
    with open('results/benchmark_timing_Ti_NIST_test.txt', 'a') as f:
        f.write('\n'.join(map(str, lines)) + '\n' '\n')


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
