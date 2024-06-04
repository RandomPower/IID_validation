import collections
import logging
import math
import os
import pathlib

from tqdm import tqdm

from . import config, plot, read, save

# Configure per-module logger
logger = logging.getLogger(f"IID_validation.{pathlib.Path(__file__).stem}")


def count_symbol_occurrences(input_file: str) -> tuple[dict[int, int], int]:
    """Calculates the number of symbols occurrences and the total number of symbols in a file.

    Parameters
    ----------
    input_file : str
        binary file

    Returns
    -------
    dict of int: int, int
        occurrences of the symbols, total number of symbols
    """
    symbols_occ_temp = collections.Counter()
    n_symbols = 0

    # Calculate number of chunks ahead of time to show loop information
    file_len = os.path.getsize(input_file)
    n_chunks = (file_len // read.DEFAULT_CHUNK_LEN) + 1

    for chunk in tqdm(read.read_file_chunks(input_file), total=n_chunks, desc="Reading input file in chunks"):
        S = read.symbols_from_bytes(chunk)
        symbols_occ_temp.update(S)
        n_symbols += len(S)

    symbols_occ = dict(sorted(symbols_occ_temp.items()))

    return symbols_occ, n_symbols


def calculate_min_entropy(symbols_occ: dict[int, int], n_symbols: int) -> tuple[list[float], float, float, float]:
    """Calculates the min-entropy, and its binomial error, using a RaP definition and min-entropy according to the NIST
    definition.

    Parameters
    ----------
    symbols_occ : dict of int: int
        occurrences of symbols
    n_symbols : int
        total number of symbols

    Returns
    -------
    list of float, float, float, float
        frequencies of the symbols, min-entropy, error on min-entropy, NIST min-entropy
    """
    frequencies = [symbols_occ[x] / n_symbols for x in symbols_occ]

    p_max = max(frequencies)
    # Compute RaP min-entropy and error
    H_min = -math.log2(p_max)
    H_min_sigma = math.sqrt(p_max * (1 - p_max) / n_symbols) / (p_max * math.log(2))
    # Compute NIST min-entropy
    # The NIST definition of H_min does not have an associated error
    p_upper = min([1, p_max + 2.576 * math.sqrt(p_max * (1 - p_max) / (n_symbols - 1))])
    H_min_NIST = -math.log2(p_upper)

    return frequencies, H_min, H_min_sigma, H_min_NIST


def min_entropy_function(conf: config.Config) -> None:
    """Calculates the min-entropy of the input file and produces a plot of its symbol frequency.

    Parameters
    ----------
    conf : config.Config
        application configuration parameters
    """
    logger.debug("Begin entropy calculation")
    symbols_occ, n_symbols = count_symbol_occurrences(conf.input_file)
    logger.debug("Symbols counted")
    frequencies, H_min, H_min_sigma, H_min_NIST = calculate_min_entropy(symbols_occ, n_symbols)
    logger.debug("Entropy calculated")
    logger.debug("Plot the symbols frequencies")
    plot.min_entropy(symbols_occ, frequencies, n_symbols, H_min, H_min_sigma, H_min_NIST)
    logger.debug("Save symbols occurrences and min-entropy values")
    save.save_entropy(conf.input_file, symbols_occ, n_symbols, H_min, H_min_sigma, H_min_NIST)
    logger.info("RaP min-entropy %s +- %s, NIST min-entropy %s", H_min, H_min_sigma, H_min_NIST)
    logger.debug("Entropy calculation completed")
