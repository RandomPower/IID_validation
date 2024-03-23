import os
import time
import sys
import numpy as np
from datetime import datetime
import time
from functools import wraps
from pathos.multiprocessing import ProcessPool as Pool
from concurrent.futures import ProcessPoolExecutor, as_completed
import logging
from architecture.utils.read import read_file
from architecture.utils.shuffles import FY_shuffle, shuffle_from_file
from architecture.utils.useful_functions import (
    execute_function,
    benchmark_timing,
    save_failure_test,
    save_test_values,
    get_next_run_number,
)
from architecture.utils.plot import scatterplot_TxTi, histogram_TxTi
from architecture.utils.config import (
    file_info,
    config_info,
    file,
    n_symbols,
    n_sequences,
    n_symbols_stat,
    test_list,
    distribution_test_index,
    bool_statistical_analysis,
    bool_test_NIST,
    test_list_indexes,
    bool_pvalue,
    p,
    bool_shuffle_NIST,
    see_plots,
    ref_numbers,
)
from architecture.statistical_analysis.counters_FYShuffle_Tx import FY_Tx
from architecture.statistical_analysis.counters_Random_Tx import Random_Tx
from architecture.statistical_analysis.counters_FYShuffle_TjNorm import FY_TjNorm
from architecture.statistical_analysis.counters_Random_TjNorm import Random_TjNorm
from architecture.statistical_analysis.comparison_counters_FyR import comparison_scatterplot

np.set_printoptions(suppress=True, threshold=np.inf, linewidth=np.inf, formatter={"float": "{:0.6f}".format})

"""
Parallelizzo il numero di sequenze estraendo 10.000 risultati --> chiamando una funzione esterna che chiama i test
Faccio un executor esterno che prende le
"""


def execute_test_suite(sequence):
    T = []
    for test_index in test_list_indexes:
        if test_index in [8, 9] and bool_pvalue:
            # If bool_pvalue is True, p_values is expected to be a list. Iterate over it.
            for p_value in p:
                result = execute_function(test_list[test_index], sequence, p_value)
                T.append(result)
        else:
            # For other cases or if bool_pvalue is False, execute the function with p_values directly.
            result = execute_function(test_list[test_index], sequence, p)
            T.append(result)
    return T


# execute_test_suite -->
# -> [0, 1, 5, 6.7, ...] come con i valori di Tx


def FY_test_mode_parallel(seq):
    Ti = []
    with ProcessPoolExecutor() as executor:
        futures = []
        for iteration in range(n_sequences):
            s_shuffled = FY_shuffle(seq.copy())
            """for k in test_list_indexes:
                if k in [8, 9]:
                    # Ensure p is passed as a list to be iterable within execute_test
                    future = executor.submit(execute_test, k, s_shuffled)
                else:
                    future = executor.submit(execute_test, k, s_shuffled)
                futures.append(future)"""
            future = executor.submit(execute_test_suite, s_shuffled)
            futures.append(future)

        completed = 0
        total_futures = len(futures)
        for future in as_completed(futures):
            Ti.append(future.result())
            completed += 1
            percentage_complete = (completed / total_futures) * 100
            sys.stdout.write(f"\rProgress: {percentage_complete:.2f}%")
            sys.stdout.flush()
    return Ti


##########  MAIN TEST  ###########
def main():
    file_info()
    config_info()
    if bool_test_NIST:
        logging.debug("NIST TEST")
        logging.debug("Process started")
        t_start = time.process_time()
        S = read_file(file=file, n_symbols=n_symbols)
        logging.debug("Sequence calculated: S")

        logging.debug("Calculating for each test the reference statistic: Tx")
        Tx = []
        for k in test_list_indexes:
            if k == 8 or k == 9:
                if bool_pvalue:
                    T = [execute_function(test_list[k], S, i) for i in p]
                    Tx += (e for e in T)
                else:
                    Tx.append(execute_function(test_list[k], S, p))
            else:
                Tx.append(execute_function(test_list[k], S, None))
        logging.debug("Reference statistics calculated!")
        logging.debug("Calculating each test statistic for each shuffled sequence: Ti")
        t0 = time.process_time()
        Ti = FY_test_mode_parallel(S)
        ti = time.process_time() - t0
        # tf = time.strftime("%H:%M:%S.{}".format(str(ti % 1)[2:])[:11_parallelized], time.gmtime(ti))
        benchmark_timing(ti, "parallelizing")
        logging.debug("Shuffled sequences Ti statistics calculated")
        C0 = [0 for k in range(len(Tx))]
        C1 = [0 for k in range(len(Tx))]

        for u in range(len(Tx)):
            a = Tx[u]
            for t in range(n_sequences):
                b = Ti[t][u]
                if Tx[u] > Ti[t][u]:
                    C0[u] += 1
                if Tx[u] == Ti[t][u]:
                    C1[u] += 1

        logging.debug(f"C0 = {C0}")
        logging.debug(f"C1 = {C1}")

        IID = True
        for b in range(len(Tx)):
            # if any(C0[b] + C1[b] <= 5 or C0[b] >= 9995 b in range(len(Tx))):
            if (C0[b] + C1[b] <= 5) or (C0[b] >= 9995):
                IID = False
                break
        if IID:
            logging.info("IID assumption validated")
        else:
            logging.info("IID assumption rejected")
        tu = time.process_time() - t_start
        logging.debug("Total process time = ", tu)
        
        # plots
        if see_plots:
            sc_dir = "results/plots/scatterplot_TxTi"
            hist_dir = "results/plots/histogram_TxTi"
            current_run_date = datetime.now().strftime("%Y-%m-%d")
            dir_sc_run = os.path.join(sc_dir, current_run_date, str(get_next_run_number(sc_dir, current_run_date)))
            dir_hist_run = os.path.join(
                hist_dir, current_run_date, str(get_next_run_number(hist_dir, current_run_date))
            )

            # Ensure the directory exists
            os.makedirs(dir_sc_run, exist_ok=True)
            os.makedirs(dir_hist_run, exist_ok=True)

            Ti_transposed = np.transpose(Ti)
            for t in range(len(Tx)):
                if bool_pvalue:
                    # Handle the special case for test 8 ('periodicity')
                    if 8 <= t <= 12:
                        p_index = t - 8  # Adjust index to map to the correct p value
                        test_name = f"{test_list[8]} (p={p[p_index]})"
                    # Handle the special case for test 9 ('covariance')
                    elif 13 <= t <= 17:
                        p_index = t - 13  # Adjust index to map to the correct p value
                        test_name = f"{test_list[9]} (p={p[p_index]})"  # Append the corresponding p value
                    # For the values that should correspond to test 10 ('compression')
                    elif t == 18:
                        test_name = test_list[10]  # Direct mapping for 'compression'
                    else:
                        # Direct mapping for other tests
                        test_name = test_list[t]
                    histogram_TxTi(Tx[t], Ti_transposed[t], test_name, dir_hist_run)
                    scatterplot_TxTi(Tx[t], Ti_transposed[t], test_name, dir_sc_run)
                else:
                    histogram_TxTi(Tx[t], Ti_transposed[t], test_list[t], dir_hist_run)
                    scatterplot_TxTi(Tx[t], Ti_transposed[t], test_list[t], dir_sc_run)

    if bool_statistical_analysis:
        logging.debug("----------------------------------------------------------------\n \n")
        logging.debug(f"STATISTICAL ANALYSIS FOR TEST {test_list[distribution_test_index]}")
        t_start = time.process_time()
        S = read_file(file=file, n_symbols=n_symbols_stat)
        logging.debug("Sequence calculated: S")
        with ProcessPoolExecutor() as executor:
            tasks = [
                executor.submit(FY_Tx, S),
                executor.submit(FY_TjNorm, S),
                executor.submit(Random_Tx, S),
                executor.submit(Random_TjNorm, S),
            ]
            # Wait for all tasks to complete
            for task in tasks:
                task.result()

        # Comparison
        comparison_scatterplot()
        logging.debug("Statistical analysis completed.")


if __name__ == "__main__":
    main()
