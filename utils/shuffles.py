import permutation_tests
import utils.config
import utils.useful_functions


def shuffle_from_file(file, ind, n_symb, n_seq):
    """Reads a sequence of bytes from a binary file and transforms it into a sequence of symbols by
    applying a masking process.

    Parameters
    ----------
    file : str
        the input binary file
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
    with open(file, "rb") as f:
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
            ind += n_symb / 2

            # TO DO: exception

        return sequences


def shuffle_from_file_Norm(file, index, n_symb, n_seq, test: int, conf: utils.config.Config):
    """Version of shuffle_from_file function for normalized Tj.
    The sequence it reads has the same result T on a given test as the previous
    sequence (T(j-1)), it discards it and passes to the next sequence. This is because for Tj normalized we want the
    counters distribution to be a binomial one with probability 1/2, so we want to ignore the cases = and only have
    the options > or <. To do so this function also needs to compute the T (aka test(seq)): it therefore gives them
    back as well, so that there is no need to compute them again. The output are two: the list of sequences and the list
     of the Ti on those sequences.

    TODO: WRITE THE SUMMARY BETTER

    Parameters
    ----------
    file : str
        the input binary file
    index : int
        position where to read in the file
    n_symb : int
        number of symbols
    n_seq : int
        number of sequences
    test : int
        test index to be executed
    conf : utils.config.Config
        application configuration parameters

    Returns
    -------
    tuple of (list of lists of int, list of int)
        sequences of lists of symbols, Ti test values calculated on the shuffled sequences
    """
    with open(file, "rb") as f:
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
        index += n_symb / 2

        if test in [8, 9]:
            t = permutation_tests.tests[test].run(S, conf.stat.p_value)
            Ti.append(t)
        else:
            t = permutation_tests.tests[test].run(S)
            Ti.append(t)
        sequences.append(S)

        z = 1
        while z < n_seq:
            f.seek(int(index))
            sequence_size = int(n_symb / 2)
            sequence = f.read(sequence_size)

            S = []
            for i in sequence:
                symbol1 = i >> 4
                S.append(symbol1)
                symbol2 = i & 0b00001111
                S.append(symbol2)

            index += n_symb / 2

            if test in [8, 9]:
                t = permutation_tests.tests[test].run(S, conf.stat.p_value)
            else:
                t = permutation_tests.tests[test].run(S)

            if t == Ti[z - 1]:
                continue
            else:
                Ti.append(t)
                sequences.append(S)
                z += 1

        return sequences, Ti
