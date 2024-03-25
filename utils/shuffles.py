import random
from utils.config import input_file, step, distribution_test_index, test, bool_pvalue, p_value_stat
from utils.useful_functions import execute_function


# %matplotlib inline


def FY_shuffle(sequence):
    """Generates a shuffled sequence using Fisher-Yates algorithm

    Parameters
    ----------
    sequence : list of int
        sequence of sample values

    Returns
    -------
    list of int
        shuffled sequence
    """
    for i in range(len(sequence) - 1, 0, -1):
        j = random.randint(0, i)
        temp = sequence[i]
        sequence[i] = sequence[j]
        sequence[j] = temp
    return sequence


# shuffle direttamente da file per ottenere sequenze senza usare FY
def shuffle_from_file(ind, n_symb, n_seq):
    """Reads a sequence of bytes from a binary file and transforms it into a sequence of symbols by 
    applying a masking process.

    Parameters
    ----------
    ind : int
        position where to read in the file
    n_symb : int
        number of symbols
    n_seq : int
        number of sequences

    Returns
    -------
    list of int
        sequences of lists of symbols
    """
    with open(input_file, "rb") as f:
        sequences = []
        for z in range(n_seq):
            # Move to the current offset
            f.seek(int(ind))

            # Read the sequence_size bytes
            sequence_size = int(n_symb / 2)
            sequence = f.read(sequence_size)

            S = []
            for i in sequence:
                symbol1 = i >> 4
                S.append(symbol1)
                symbol2 = i & 0b00001111
                S.append(symbol2)

            sequences.append(S)

            # Increment the offset by step-byte
            ind += step

            # TO DO: exception
        return sequences


def shuffle_from_file_Norm(index, n_symb, n_seq, test):
    """Version of shuffle_from_file function for normalized Tj. 
    The sequence it reads has the same result T on a given test as the previous
    sequence (T(j-1)), it discards it and passes to the next sequence. This is because for Tj normalized we want the
    counters_oli distribution to be a binomial one with probability 1/2, so we want to ignore the cases = and only have
    the options > or <. To do so this function also needs to compute the T (aka test(seq)): it therefore gives them
    back as well, so that there is no need to compute them again (this however changes the main as well, I don't know
    if it's howerall convenient). The otput are two: the list of sequences and the list of the Ti on those sequences.

    TO DO: WRITE THE SUMMARY BETTER

    Parameters
    ----------
    index : int
        position where to read in the file
    n_symb : int
        number of symbols
    n_seq : int
        number of sequences
    test : str
        function name to be executed

    Returns
    -------
    tuple of (list of lists of int, list of int)
        sequences of lists of symbols, Ti test values calculated on the shuffled sequences
    """
    with open(input_file, "rb") as f:
        sequences = []
        Ti = []

        # Read first sequence
        f.seek(int(index))
        sequence_size = int(n_symb / 2)
        sequence = f.read(sequence_size)
        S = []
        for i in sequence:
            symbol1 = i >> 4
            S.append(symbol1)
            symbol2 = i & 0b00001111
            S.append(symbol2)
        index += step

        if distribution_test_index == 8 or distribution_test_index == 9:
            t = execute_function(test, S, p_value_stat)
            Ti.append(t)
        else:
            t = execute_function(test, S, None)
            Ti.append(t)
        sequences.append(S)

        z = 1
        while z < n_seq:
            # Move to the current offset
            f.seek(int(index))

            # Read the sequence_size bytes
            sequence_size = int(n_symb / 2)
            sequence = f.read(sequence_size)

            S = []
            for i in sequence:
                symbol1 = i >> 4
                S.append(symbol1)
                symbol2 = i & 0b00001111
                S.append(symbol2)

            index += step

            if distribution_test_index == 8 or distribution_test_index == 9:
                t = execute_function(test, S, p_value_stat)
            else:
                t = execute_function(test, S, None)

            if t == Ti[z - 1]:
                continue
            else:
                Ti.append(t)
                sequences.append(S)
                z += 1

        return sequences, Ti
