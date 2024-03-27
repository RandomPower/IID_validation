"""
CONFIGURATION FILE - CHANGE VARIABLES TO RUN THE DESIRED CONFIGURATION
"""

import logging
import os
import tomllib


def parse_config_file(file_path: str) -> dict:
    """Parse the specified file into a Python dictionary

    Args:
        file_path (str): the path of the configuration file.

    Returns:
        dict: a dictionary containing all the configuration values,
            or an empty dictionary if the configuration file cannot
            be parsed.

    Raises:
        IOError: If the file specified by 'file_path' cannot be opened or read.
        Exception: If any other unexpected error occurs during parsing.
    """
    try:
        with open(file_path, "rb") as f:
            config_data: dict = tomllib.load(f)
        return config_data
    except IOError as e:
        print(f"Error opening or reading config file: {e}")
        return {}
    except Exception as e:
        print(f"Error parsing config file: {e}")
        return {}


config_data: dict = parse_config_file("./conf.toml")

# GLOBAL VARIABLES
input_file = os.path.abspath(os.path.join("getbits_20230401_195315_RAW_BITS.BIN"))
bool_test_NIST = True
bool_statistical_analysis = False

# NIST TEST VARIABLES
n_symbols = 100
n_sequences = 100
bool_shuffle_NIST = True  # --> if True: FY shuffle, if False: use random sampling from file
bool_first_seq = True  # --> if True: reference sequence read from beginning; if False: reference sequence from the end
bool_pvalue = False  # --> if True: NIST values, if False: user chooses value
see_plots = False

if bool_pvalue:
    p = [1, 2, 8, 16, 32]  # NIST values
else:
    p = 2  # User sets preferred value


# STATISTICAL ANALYSIS VARIABLES
n_sequences_stat = 200
n_symbols_stat = 1000
n_iterations_c_stat = 500
distribution_test_index = 6  # Select which test index for counter distribution

bool_shuffle_stat = True  # --> if True: FY shuffle, if False: use random sampling from file

p_value_stat = 2  # User sets preferred value
ref_numbers = [1, 3, 4]  # Select which test indexes for shuffle/random comparison

# GLOBAL VARIABLES
test_list_indexes = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
]  # Select which tests to test IID assumption
step = n_symbols / 2  # step in reading bin file

# Test list
test_list = {
    0: "excursion_test",
    1: "n_directional_runs",
    2: "l_directional_runs",
    3: "n_median_runs",
    4: "l_median_runs",
    5: "n_increases_decreases",
    6: "avg_collision",
    7: "max_collision",
    8: "periodicity",
    9: "covariance",
    10: "compression",
}

# test chosen for counters distribution
test = test_list[distribution_test_index]


def file_info():
    f = open(input_file, "r+b")
    f.seek(0, 2)
    size = f.tell()
    logging.debug("FILE INFO")
    logging.debug("Size of file is: %s bytes", size)
    logging.debug("Number of symbols per sequence for counters analysis: %s", n_symbols_stat)
    logging.debug("Number of sequences wanted for counters analysis: %s", n_sequences_stat)
    max_symbols = size * 2  # total number of symbols in the file
    max_sequences = max_symbols / n_symbols_stat
    logging.debug("Maximum sequences that can be generated from the file: %s", max_sequences)
    tot_seqs = n_iterations_c_stat * n_sequences_stat
    logging.debug("Total sequences necessary = %s", tot_seqs)
    if not bool_shuffle_stat:
        if tot_seqs <= max_sequences:
            logging.debug("SHUFFLE FROM FILE ALLOWED WITH THIS FILE")
        else:
            logging.error("SHUFFLE FROM FILE NOT ALLOWED WITH THIS FILE")
            exit(-1)
    logging.debug("----------------------------------------------------------------\n")


def config_info():
    logging.debug("CONFIG INFO - NIST")
    logging.debug("Number of symbols per sequence = %s", n_symbols)
    logging.debug("Number of shuffled sequences = %s", n_sequences)
    ts = [test_list.get(i) for i in test_list_indexes]
    logging.debug("Tests for entropy validation selected: %s", ts)
    if bool_first_seq:
        logging.debug("Reference sequence read from the beginning of the file")
    else:
        logging.debug("Reference sequence read from the end of the file")
    if bool_pvalue:
        logging.debug("p parameter used: NIST")
    else:
        logging.debug("p parameter used: user value \n")

    logging.debug("\nCONFIG INFO - STATISTICAL ANALYSIS")
    logging.debug("Number of symbols per sequence = %s", n_symbols_stat)
    logging.debug("Number of shuffled sequences = %s", n_sequences_stat)
    logging.debug("Number of iterations for counter: %s", n_iterations_c_stat)
    logging.debug("Test selected for counter distribution analysis: %s", test)
    comp = [test_list.get(i) for i in ref_numbers]
    logging.debug("Tests selected test for shuffle/random comparison: %s", comp)
    logging.debug("p parameter used: user value: %s", p_value_stat)
    logging.debug("----------------------------------------------------------------\n \nMAIN")
