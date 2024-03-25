import os

import utils.config


def read_file(file, n_symbols):
    """
    Function that reads from binary file the sequence of n_symbols
    :param file: path to file
    :param n_symbols: number of symbols to read
    :return: S sequence
    """
    with open(file, "r+b") as f:
        tot_bytes = int(n_symbols / 2)
        if utils.config.bool_first_seq:
            my_bytes = f.read(tot_bytes)
        else:
            f.seek(-tot_bytes, os.SEEK_END)
            my_bytes = f.read(tot_bytes)
    S = []
    for i in my_bytes:
        symbol1 = i >> 4
        S.append(symbol1)
        symbol2 = i & 0b00001111
        S.append(symbol2)

    return S
