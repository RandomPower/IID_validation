import concurrent.futures
import datetime
import logging
import os
import sys
import time

import numpy as np

import statistical_analysis.comparison_counters_FyR
import statistical_analysis.counters_FYShuffle_TjNorm
import statistical_analysis.counters_FYShuffle_Tx
import statistical_analysis.counters_Random_TjNorm
import statistical_analysis.counters_Random_Tx
import utils.config
import utils.plot
import utils.read
import utils.shuffles
import utils.useful_functions

logging.basicConfig(
    filename="IID_validation.log", filemode="w", format="%(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

np.set_printoptions(suppress=True, threshold=np.inf, linewidth=np.inf, formatter={"float": "{:0.6f}".format})


def execute_test_suite(sequence):
    """Executes NIST test suite on a given sequence

    Parameters
    ----------
    sequence : list of int
        sequence of sample values

    Returns
    -------
    float
        executed test output
    """
    T = []
    for test_index in utils.config.config_data['global']['test_list_indexes']:
        if int(test_index) in [8, 9] and utils.config.config_data['nist_test']['bool_pvalue']:
            # If bool_pvalue is True, p_values is expected to be a list. Iterate over it.
            for p_value in utils.config.config_data['nist_test']['p']:
                result = utils.useful_functions.execute_function(utils.config.config_data['test_list'][test_index], sequence, p_value)
                T.append(result)
        else:
            # For other cases or if bool_pvalue is False, execute the function with p_values directly.
            result = utils.useful_functions.execute_function(
                utils.config.config_data['test_list'][test_index], sequence, utils.config.p
            )
            T.append(result)
    return T


def FY_test_mode_parallel(seq):
    """Executes NIST test suite on shuffled sequence in parallel along n_sequences iterations

    Parameters
    ----------
    sequence : ist of int
        sequence of sample values

    Returns
    -------
    list of float
        list of test outputs
    """
    Ti = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for iteration in range(utils.config.config_data['nist_test']['n_sequences']):
            s_shuffled = utils.shuffles.FY_shuffle(seq.copy())
            future = executor.submit(execute_test_suite, s_shuffled)
            futures.append(future)

        completed = 0
        total_futures = len(futures)
        for future in concurrent.futures.as_completed(futures):
            Ti.append(future.result())
            completed += 1
            percentage_complete = (completed / total_futures) * 100
            sys.stdout.write(f"\rProgress: {percentage_complete:.2f}%")
            sys.stdout.flush()
    return Ti


def main():
    utils.config.file_info()
    utils.config.config_info()
    if utils.config.config_data['global']['bool_test_NIST']:
        logging.debug("NIST TEST")
        logging.debug("Process started")
        t_start = time.process_time()
        S = utils.read.read_file(file=utils.config.config_data['global']['input_file'], n_symbols=utils.config.config_data['nist_test']['n_symbols'])
        logging.debug("Sequence calculated: S")

        logging.debug("Calculating for each test the reference statistic: Tx")
        Tx = []
        for k in utils.config.config_data['global']['test_list_indexes']:
            if k == '8' or k == '9':
                if utils.config.config_data['nist_test']['bool_pvalue']:
                    T = [
                        utils.useful_functions.execute_function(utils.config.config_data['test_list'][k], S, i)
                        for i in utils.config.config_data['nist_test']['p']
                    ]
                    Tx += (e for e in T)
                else:
                    Tx.append(utils.useful_functions.execute_function(utils.config.config_data['test_list'][k], S, utils.config.p))
            else:
                Tx.append(utils.useful_functions.execute_function(utils.config.config_data['test_list'][k], S, None))
        logging.debug("Reference statistics calculated!")
        logging.debug("Calculating each test statistic for each shuffled sequence: Ti")
        t0 = time.process_time()
        Ti = FY_test_mode_parallel(S)
        ti = time.process_time() - t0
        utils.useful_functions.benchmark_timing(ti, "parallelizing")
        logging.debug("Shuffled sequences Ti statistics calculated")
        C0 = [0 for k in range(len(Tx))]
        C1 = [0 for k in range(len(Tx))]

        for u in range(len(Tx)):
            for t in range(utils.config.config_data['nist_test']['n_sequences']):
                if Tx[u] > Ti[t][u]:
                    C0[u] += 1
                if Tx[u] == Ti[t][u]:
                    C1[u] += 1

        logging.debug("C0 = %s", C0)
        logging.debug("C1 = %s", C1)

        IID = True
        for b in range(len(Tx)):
            if (C0[b] + C1[b] <= 5) or (C0[b] >= 9995):
                IID = False
                break
        if IID:
            logging.info("IID assumption validated")
        else:
            logging.info("IID assumption rejected")
        tu = time.process_time() - t_start
        logging.debug("Total process time = %s", tu)
        # plots
        if utils.config.config_data['nist_test']['see_plots']:
            sc_dir = "results/plots/scatterplot_TxTi"
            hist_dir = "results/plots/histogram_TxTi"
            current_run_date = datetime.datetime.now().strftime("%Y-%m-%d")
            dir_sc_run = os.path.join(
                sc_dir, current_run_date, str(utils.useful_functions.get_next_run_number(sc_dir, current_run_date))
            )
            dir_hist_run = os.path.join(
                hist_dir, current_run_date, str(utils.useful_functions.get_next_run_number(hist_dir, current_run_date))
            )

            # Ensure the directory exists
            os.makedirs(dir_sc_run, exist_ok=True)
            os.makedirs(dir_hist_run, exist_ok=True)

            Ti_transposed = np.transpose(Ti)
            for t in range(len(Tx)):
                if utils.config.config_data['nist_test']['bool_pvalue']:
                    # Handle the special case for test 8 ('periodicity')
                    if 8 <= t <= 12:
                        p_index = t - 8  # Adjust index to map to the correct p value
                        test_name = f"{utils.config.config_data['test_list']['8']} (p={utils.config.config_data['nist_test']['p'][p_index]})"
                    # Handle the special case for test 9 ('covariance')
                    elif 13 <= t <= 17:
                        p_index = t - 13  # Adjust index to map to the correct p value
                        test_name = f"{utils.config.config_data['test_list']['9']} (p={utils.config.config_data['nist_test']['p'][p_index]})"
                    # For the values that should correspond to test 10 ('compression')
                    elif t == 18:
                        test_name = utils.config.config_data['test_list']['10']  # Direct mapping for 'compression'
                    else:
                        # Direct mapping for other tests
                        test_name = utils.config.config_data['test_list'][str(t)]
                    utils.plot.histogram_TxTi(Tx[t], Ti_transposed[t], test_name, dir_hist_run)
                    utils.plot.scatterplot_TxTi(Tx[t], Ti_transposed[t], test_name, dir_sc_run)
                else:
                    utils.plot.histogram_TxTi(Tx[t], Ti_transposed[t], utils.config.config_data['test_list'][str(t)], dir_hist_run)
                    utils.plot.scatterplot_TxTi(Tx[t], Ti_transposed[t], utils.config.config_data['test_list'][str(t)], dir_sc_run)

    if utils.config.config_data['global']['bool_statistical_analysis']:
        logging.debug("----------------------------------------------------------------\n \n")
        logging.debug("STATISTICAL ANALYSIS FOR TEST %s", utils.config.config_data['test_list'][utils.config.config_data['statistical_analysis']['distribution_test_index']])
        t_start = time.process_time()
        S = utils.read.read_file(file=utils.config.config_data['global']['input_file'], n_symbols=utils.config.config_data['statistical_analysis']['n_symbols_stat'])
        logging.debug("Sequence calculated: S")
        with concurrent.futures.ProcessPoolExecutor() as executor:
            tasks = [
                executor.submit(statistical_analysis.counters_FYShuffle_Tx.FY_Tx, S),
                executor.submit(statistical_analysis.counters_FYShuffle_TjNorm.FY_TjNorm, S),
                executor.submit(statistical_analysis.counters_Random_Tx.Random_Tx, S),
                executor.submit(statistical_analysis.counters_Random_TjNorm.Random_TjNorm, S),
            ]
            # Wait for all tasks to complete
            for task in tasks:
                task.result()

        statistical_analysis.comparison_counters_FyR.comparison_scatterplot()
        logging.debug("Statistical analysis completed.")


if __name__ == "__main__":
    main()
