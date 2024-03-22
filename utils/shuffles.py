import random
from architecture.utils.config import file, step, distribution_test_index, test, bool_pvalue, p_value_stat
from architecture.utils.useful_functions import execute_function


# %matplotlib inline


def FY_shuffle(sequence):
    """
    This function uses the Fisher-Yates method to generate the shuffled sequence
    :param sequence: sequence to be shuffles
    :return: shuffled sequence
    """
    for i in range(len(sequence) - 1, 0, -1):
        j = random.randint(0, i)
        temp = sequence[i]
        sequence[i] = sequence[j]
        sequence[j] = temp
    return sequence


# shuffle direttamente da file per ottenere sequenze senza usare FY
def shuffle_from_file(ind, n_symb, n_seq):
    """
    This function read sequences from file

    :param n_symb:
    :param ind: index in the file
    :param n_symbols: number of symols per sequence
    :param n_sequences: number of sequences
    :return: shuffled sequences
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
    """
    Shuffle from file normalized

    This function is a modification of shuffle_from_file used for normalized Tj counters_oli. It takes the same input
    index as shuffle_from_file, but if the sequence it reads has the same result T on a given test as the previous
    sequence (T(j-1)), it discards it and passes to the next sequence. This is because for Tj normalized we want the
    counters_oli distribution to be a binomial one with probability 1/2, so we want to ignore the cases = and only have
    the options > or <. To do so this function also needs to compute the T (aka test(seq)): it therefore gives them
    back as well, so that there is no need to compute them again (this however changes the main as well, I don't know
    if it's howerall convenient). The otput are two: the list of sequences and the list of the Ti on those sequences.

    :param index: index in the file
    :param n_symbols: number of symbols in the sequence
    :param n_sequences: number of sequences
    :param test: test on which perform the statistical analysis
    :return: shuffled sequences, reference statistics on the shuffled sequences
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
