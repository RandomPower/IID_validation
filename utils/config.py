"""
CONFIGURATION FILE - CHANGE VARIABLES TO RUN THE DESIRED CONFIGURATION
"""

import logging
import tomllib

import permutation_tests


def parse_config_file(file_path: str) -> dict:
    """Parse the specified file into a Python dictionary

    Args:
        file_path (str): the path of the configuration file.

    Returns:
        dict: a dictionary containing all the configuration values,
            or an empty dictionary if the configuration file cannot
            be parsed.
    """
    try:
        with open(file_path, "rb") as f:
            config_data: dict = tomllib.load(f)
        return config_data
    except IOError as e:
        logging.error("Unable to open or read config file: %s", e)
        return {}
    except Exception as e:
        logging.error("Unable to parse config file: %s", e)
        return {}


config_data = parse_config_file("conf.toml")

if config_data["nist_test"]["bool_pvalue"]:
    # NIST values
    p = [1, 2, 8, 16, 32]
else:
    # User sets preferred value
    p = [2]

# step in reading bin file
step = config_data["nist_test"]["n_symbols"] / 2


def file_info():
    f = open(config_data["global"]["input_file"], "r+b")
    f.seek(0, 2)
    size = f.tell()
    logging.debug("FILE INFO")
    logging.debug("Size of file is: %s bytes", size)
    logging.debug(
        "Number of symbols per sequence for counters analysis: %s",
        config_data["statistical_analysis"]["n_symbols_stat"],
    )
    logging.debug(
        "Number of sequences wanted for counters analysis: %s", config_data["statistical_analysis"]["n_sequences_stat"]
    )
    # total number of symbols in the file
    max_symbols = size * 2
    max_sequences = max_symbols / config_data["statistical_analysis"]["n_symbols_stat"]
    logging.debug("Maximum sequences that can be generated from the file: %s", max_sequences)
    tot_seqs = (
        config_data["statistical_analysis"]["n_iterations_c_stat"]
        * config_data["statistical_analysis"]["n_sequences_stat"]
    )
    logging.debug("Total sequences necessary = %s", tot_seqs)
    if not config_data["statistical_analysis"]["bool_shuffle_stat"]:
        if tot_seqs <= max_sequences:
            logging.debug("SHUFFLE FROM FILE ALLOWED WITH THIS FILE")
        else:
            logging.error("SHUFFLE FROM FILE NOT ALLOWED WITH THIS FILE")
            exit(-1)
    logging.debug("----------------------------------------------------------------\n")


def config_info():
    logging.debug("CONFIG INFO - NIST")
    logging.debug("Number of symbols per sequence = %s", config_data["nist_test"]["n_symbols"])
    logging.debug("Number of shuffled sequences = %s", config_data["nist_test"]["n_sequences"])
    ts = [permutation_tests.tests[i].name for i in config_data["global"]["test_list_indexes"]]
    logging.debug("Tests for entropy validation selected: %s", ts)
    if config_data["nist_test"]["bool_first_seq"]:
        logging.debug("Reference sequence read from the beginning of the file")
    else:
        logging.debug("Reference sequence read from the end of the file")
    if config_data["nist_test"]["bool_pvalue"]:
        logging.debug("p parameter used: NIST")
    else:
        logging.debug("p parameter used: user value \n")

    logging.debug("\nCONFIG INFO - STATISTICAL ANALYSIS")
    logging.debug("Number of symbols per sequence = %s", config_data["statistical_analysis"]["n_symbols_stat"])
    logging.debug("Number of shuffled sequences = %s", config_data["statistical_analysis"]["n_sequences_stat"])
    logging.debug("Number of iterations for counter: %s", config_data["statistical_analysis"]["n_iterations_c_stat"])
    logging.debug(
        "Test selected for counter distribution analysis: %s",
        permutation_tests.tests[config_data["statistical_analysis"]["distribution_test_index"]].name,
    )
    comp = [permutation_tests.tests[i].name for i in config_data["statistical_analysis"]["ref_numbers"]]
    logging.debug("Tests selected test for shuffle/random comparison: %s", comp)
    logging.debug("p parameter used: user value: %s", config_data["statistical_analysis"]["p_value_stat"])
    logging.debug("----------------------------------------------------------------\n \nMAIN")
