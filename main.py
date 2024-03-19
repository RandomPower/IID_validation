"""
ENTROPY VALIDATION ARCHITECTURE
Before running the main, fix the variables wanted in the architecture/utils/config.py file
"""

import os
import time
import numpy as np
from datetime import datetime
from tqdm import tqdm
from pathos.multiprocessing import ProcessPool as Pool
from architecture.utils.read import read_file
from architecture.utils.shuffles import FY_shuffle, shuffle_from_file
from architecture.utils.useful_functions import execute_function, benchmark_timing, save_failure_test, save_test_values, get_next_run_number
from architecture.utils.plot import scatterplot_TxTi, histogram_TxTi
from architecture.utils.config import file_info, config_info, file, n_symbols, n_sequences, n_symbols_stat, test_list, \
    distribution_test_index, bool_statistical_analysis, bool_test_NIST, test_list_indexes, bool_pvalue, p, \
    bool_shuffle_NIST, see_plots, ref_numbers
from architecture.statistical_analysis.counters_FYShuffle_Tx import FY_Tx
from architecture.statistical_analysis.counters_Random_Tx import Random_Tx
from architecture.statistical_analysis.counters_FYShuffle_TjNorm import FY_TjNorm
from architecture.statistical_analysis.counters_Random_TjNorm import Random_TjNorm
from architecture.statistical_analysis.comparison_counters_FyR import comparison_scatterplot

##########  MAIN TEST  ###########
file_info()
config_info()
np.set_printoptions(suppress=True, threshold=np.inf, linewidth=np.inf, formatter={'float': '{:0.6f}'.format})


def FY_test_mode_p(seq):
    def get_test_results():
        Tk = []
        s_shuffled = FY_shuffle(seq.copy())
        for k in test_list_indexes:
            if k == 8 or k == 9:
                if bool_pvalue:
                    for i in p:
                        T = execute_function(test_list[k], s_shuffled, i)
                        Tk.append(T)
                else:
                    Tk.append(execute_function(test_list[k], s_shuffled, p))
            else:
                Tk.append(execute_function(test_list[k], s_shuffled, None))

        return Tk

    with Pool() as p:
        Ti = p.map(lambda x: get_test_results(), range(n_sequences),
                   chunksize=n_sequences // (os.cpu_count()))
        return Ti


if bool_test_NIST:
    def FY_test_mode(seq):
        Ti = []
        for iteration in tqdm(range(n_sequences)):
            # print(f'\niteration: {iteration}')
            # t_0 = time.process_time()
            Tk = []
            s_shuffled = FY_shuffle(seq.copy())
            # print('Shuffle done!')
            # t_i = time.process_time() - t_0
            # t_f = time.strftime("%H:%M:%S.{}".format(str(t_i % 1)[2:])[:11_parallelized], time.gmtime(t_i))
            # print(f'shuffle time: {t_i}')
            for k in test_list_indexes:
                # print(f'test: {test_list[k]}')
                # t0 = time.process_time()
                if k == 8 or k == 9:
                    if bool_pvalue:
                        for i in p:
                            T = execute_function(test_list[k], s_shuffled, i)
                            Tk.append(T)
                    else:
                        Tk.append(execute_function(test_list[k], s_shuffled, p))
                else:
                    # timed(Ti.append([execute_function(test_list[k], si, None) for si in S_shuffled]))
                    Tk.append(execute_function(test_list[k], s_shuffled, None))
                # ti = time.process_time() - t0
                # tf = time.strftime("%H:%M:%S.{}".format(str(ti % 1)[2:])[:11_parallelized], time.gmtime(ti))
                # print(f'test time: {ti}')
            Ti.append(Tk)
        return Ti


    def file_mode():
        ind = 0
        S_shuffled = shuffle_from_file(ind, n_symbols, n_sequences)
        Ti = []
        print("Calculating each test statistic for each shuffled sequence: Ti")
        for k in test_list_indexes:
            if k == 8 or k == 9:
                if bool_pvalue:
                    for i in p:
                        T = [execute_function(test_list[k], si, i) for si in S_shuffled]
                        Ti.append(T)
                else:
                    Ti.append([execute_function(test_list[k], si, p) for si in S_shuffled])
            else:
                # timed(Ti.append([execute_function(test_list[k], si, None) for si in S_shuffled]))
                Ti.append([execute_function(test_list[k], si, None) for si in S_shuffled])
        return Ti


    ##########  MAIN TEST  ###########
    print("NIST TEST")
    print("Process started")
    t_start = time.process_time()
    S = read_file(file=file, n_symbols=n_symbols)
    print("Sequence calculated: S")

    print("Calculating for each test the reference statistic: Tx")
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
    print("Reference statistics calculated!")
    print("Calculating each test statistic for each shuffled sequence: Ti")
    t0 = time.process_time()
    if bool_shuffle_NIST:
        Ti = FY_test_mode(S)

    else:
        Ti = file_mode()
    ti = time.process_time() - t0
    # tf = time.strftime("%H:%M:%S.{}".format(str(ti % 1)[2:])[:11_parallelized], time.gmtime(ti))
    # benchmark_timing(ti, "non parallelizing")
    # ti = time.process_time() - t0
    # tf = time.strftime("%H:%M:%S.{}".format(str(ti % 1)[2:])[:11_parallelized], time.gmtime(ti))
    print("Shuffled sequences Ti statistics calculated")
    # print(f'Tx = {len(Tx)}')
    # print(f'Ti = {len(Ti)}')
    # save_test_values(Tx, Ti)
    # shape(Ti) = n_tests x n_iterations
    C0 = [0 for k in range(len(Tx))]
    C1 = [0 for k in range(len(Tx))]

    for u in range(len(Tx)):
        # a = Tx[u]
        for t in range(n_sequences):
            # b = Ti[t][u]
            if Tx[u] > Ti[t][u]:
                C0[u] += 1
            if Tx[u] == Ti[t][u]:
                C1[u] += 1

    print(f'C0 = {C0}')
    print(f'C1 = {C1}')

    IID = True
    for b in range(len(Tx)):
        # if any(C0[b] + C1[b] <= 5 or C0[b] >= 9995 b in range(len(Tx))):
        if (C0[b] + C1[b] <= 5) or (C0[b] >= 9995):
            IID = False
            break
    if IID:
        print("IID assumption: assume the noise")
    else:
        print("IID assumption rejected")
    tu = time.process_time() - t_start
    print("Total process time = ", tu)
    # Creates csv file to collect failures
    # save_failure_test(C0, C1, IID, tu)

    """
        Plots
    """
    if see_plots:
        sc_dir = "results/plots/scatterplot_TxTi"
        hist_dir = "results/plots/histogram_TxTi"
        current_run_date = datetime.now().strftime("%Y-%m-%d")
        dir_sc_run = os.path.join(sc_dir, current_run_date, str(get_next_run_number(sc_dir, current_run_date)))
        dir_hist_run = os.path.join(hist_dir, current_run_date, str(get_next_run_number(hist_dir, current_run_date)))

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
    print("----------------------------------------------------------------")
    print(f'STATISTICAL ANALYSIS FOR TEST {test_list[distribution_test_index]}')
    t_start = time.process_time()
    S = read_file(file=file, n_symbols=n_symbols_stat)
    print("Sequence calculated: S")
    FY_Tx(S)
    FY_TjNorm(S)
    Random_Tx(S)
    Random_TjNorm(S)

    # Comparison
    comparison_scatterplot()
    print("Analysis completed!")