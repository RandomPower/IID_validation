import bz2
import random
import statistics

import utils.config


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


def s_prime(S):
    """Generates a transformed sequence based on the comparison of consecutive elements in the input sequence.
    For each pair of consecutive elements, if the first element is greater than the second, a -1
    is appended to the new sequence; otherwise, a +1 is appended.

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    list of int
        new sequence of -1s and +1s
    """
    if len(S) == 0:
        raise Exception("Input sequence has length 0")
    if len(S) == 1:
        raise Exception("Input sequence has length 1")

    S_prime = []
    for i in range(len(S) - 1):
        if S[i] > S[i + 1]:
            S_prime.append(-1)
        else:
            S_prime.append(1)

    return S_prime


def s_prime_median(S):
    """Generates a transformed sequence where each original value is replaced with -1 if it is
    less than the median of the original sequence, or 1 if it is greater than or equal to the median

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    list of int
        new sequence of -1s and +1s
    """
    if len(S) == 0:
        raise Exception("Input sequence has length 0")

    M = statistics.median(S)
    S_prime = []
    for i in range(len(S)):
        if S[i] < M:
            S_prime.append(-1)
        else:
            S_prime.append(1)
    return S_prime


def excursion_test(S):
    """Measures how far the running sum of sample values deviates from its
    average value at each point in the sequence

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    float
        maximum deviation from the average
    """
    X = statistics.mean(S)
    cumulative_sum = 0
    D = [abs((cumulative_sum := cumulative_sum + element) - (i * X)) for i, element in enumerate(S, 1)]
    return max(D)


def n_directional_runs(S):
    """Measures the number of runs constructed using the relations between consecutive samples

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
        number of runs
    """
    S_prime = s_prime(S)

    T = 1
    for k in range(1, len(S_prime)):
        if S_prime[k] != S_prime[k - 1]:
            T += 1
    return T


def l_directional_runs(S):
    """Measures the length of the longest run constructed using the relations between
    consecutive samples

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
        length of the longest run of consecutive samples that are either strictly increasing or strictly decreasing
    """
    S_prime = s_prime(S)

    T = 0
    current_count = 1

    for k in range(0, len(S_prime) - 1):
        if S_prime[k] == S_prime[k + 1]:
            current_count += 1
        else:
            if current_count > T:
                T = current_count
                current_count = 1

    if current_count > T:
        T = current_count

    return T


def n_increases_decreases(S):
    """Measures the maximum number of increases or decreases between consecutive sample values

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
        greater number between the total counts of increases and decreases among consecutive sample values
    """
    S_prime = s_prime(S)

    count_plus = 0
    count_minus = 0

    for k in range(len(S_prime)):
        if S_prime[k] == -1:
            count_minus += 1
        else:
            count_plus += 1
    return max(count_minus, count_plus)


def n_median_runs(S):
    """Measures the number of runs that are constructed with respect to the median of the sequence

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
        number of runs
    """
    S_prime = s_prime_median(S)

    T = 1
    for i in range(1, len(S_prime)):
        if S_prime[i] != S_prime[i - 1]:
            T += 1
    return T


def l_median_runs(S):
    """Measures the length of the longest run constructed with respect to the median of the sequence

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
        length of the longest run
    """
    S_prime = s_prime_median(S)

    T = 0
    current_count = 1

    for k in range(0, len(S_prime) - 1):
        if S_prime[k] == S_prime[k + 1]:
            current_count += 1
        else:
            if current_count > T:
                T = current_count
                current_count = 1

    if current_count > T:
        T = current_count

    return T


def avg_c(S):
    """Counts the number of successive sample values until a duplicate is found

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
    average length of subsequences with unique sample values before encountering a duplicate
    """
    seen = set()
    C = []
    last_split = 0
    for i, x in enumerate(S):
        if x in seen:
            seen = set()
            C.append(i - last_split)
            last_split = i + 1
        else:
            seen.add(x)
    return statistics.mean(C) + 1


def max_c(S):
    """Counts the number of successive sample values until a duplicate is found

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
    length of the longest unique subsequence before encountering a duplicate value
    """
    seen = set()
    C = []
    last_split = 0
    for i, x in enumerate(S):
        if x in seen:
            seen = set()
            C.append(i + 1 - last_split)
            last_split = i + 1
        else:
            seen.add(x)
    return max(C) + 1


def periodicity(S, y):
    """Determines the number of periodic samples in the sequence

    Parameters
    ----------
    S : list of int
        sequence of sample values
    y : int
        lag parameter

    Returns
    -------
    int
        number of instances where an element in the sequence is equal to another element that is y positions ahead
    """
    T = 0
    for i in range(0, len(S) - y):
        if S[i] == S[i + y]:
            T += 1
    return T


def covariance(S, p):
    """Measures the strength of the lagged correlation

    Parameters
    ----------
    S : list of int
        sequence of sample values
    p : int
        lag parameter p

    Returns
    -------
    int
        sum of the products of each element in the sequence with another element that is p positions ahead
    """
    T = 0
    for i in range(len(S) - p):
        T += S[i] * S[i + p]
    return T


def compression(S):
    """Removes redundancy in the sequence, involving commonly recurring subsequences of characters.
    Encodes input data as a character string containing a list of values separated by a single
    space. Compresses the character string with the bzip2 compression algorithm

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
        length of the compressed string
    """
    S_string = " "
    for i in S:
        S_string += str(i) + " "
    t = bz2.compress(S_string.encode("utf-8"))
    return len(t)


def execute_function(function_name, S, y):
    """Calls functions to execute based on the function name provided

    Parameters
    ----------
    function_name : str
        function name to be executed
    S : list of int
        sequence of sample values
    y : int
        lag parameter p

    Returns
    -------
    int or float
        output of the executed test function
    """
    return {
        "excursion_test": lambda: excursion_test(S),
        "n_directional_runs": lambda: n_directional_runs(S),
        "l_directional_runs": lambda: l_directional_runs(S),
        "n_median_runs": lambda: n_median_runs(S),
        "l_median_runs": lambda: l_median_runs(S),
        "n_increases_decreases": lambda: n_increases_decreases(S),
        "avg_collision": lambda: avg_c(S),
        "max_collision": lambda: max_c(S),
        "periodicity": lambda: periodicity(S, y),
        "covariance": lambda: covariance(S, y),
        "compression": lambda: compression(S),
    }[function_name]()


def execute_test_suite(sequence):
    """Executes NIST test suite on a given sequence

    Parameters
    ----------
    sequence : list of int
        sequence of sample values

    Returns
    -------
    list of float
        list of tests results
    """
    T = []
    for test_index in utils.config.config_data['global']['test_list_indexes']:
        if test_index in ['8', '9'] and utils.config.config_data['nist_test']['bool_pvalue']:
            # If bool_pvalue is True, p_values is expected to be a list. Iterate over it.
            for p_value in utils.config.p:
                result = execute_function(
                    utils.config.config_data['test_list'][test_index], sequence, p_value
                )
                T.append(result)
        else:
            # For other cases or if bool_pvalue is False, execute the function with p_values directly.
            result = execute_function(
                utils.config.config_data['test_list'][test_index], sequence, utils.config.p
            )
            T.append(result)
    return T
