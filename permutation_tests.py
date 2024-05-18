import bz2
import concurrent.futures
import random
import statistics
import sys
import typing

import permutation_tests


def FY_shuffle(S):
    """Generates a shuffled sequence using Fisher-Yates algorithm

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    list of int
        shuffled sequence
    """
    for i in range(len(S) - 1, 0, -1):
        j = random.randint(0, i)
        S[i], S[j] = S[j], S[i]
    return S


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

    S_prime = [0] * (len(S) - 1)
    for i in range(len(S) - 1):
        if S[i] > S[i + 1]:
            S_prime[i] = -1
        else:
            S_prime[i] = 1

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
    S_prime = [0] * (len(S))
    for i in range(len(S)):
        if S[i] < M:
            S_prime[i] = -1
        else:
            S_prime[i] = 1
    return S_prime


def _excursion(S):
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
    D = [abs((cumulative_sum := cumulative_sum + element) - (i * X)) for i, element in enumerate(S, 1)]  # noqa: F841
    return max(D)


def _n_directional_runs(S):
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


def _l_directional_runs(S):
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


def _n_increases_decreases(S):
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


def _n_median_runs(S):
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


def _l_median_runs(S):
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


def _avg_collision(S):
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


def _max_collision(S):
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


def _periodicity(S, y):
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


def _covariance(S, p):
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


def _compression(S):
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
    S_string = " ".join(map(str, S))
    t = bz2.compress(S_string.encode("utf-8"))
    return len(t)


_Test = typing.NamedTuple("Test", [("id", int), ("name", str), ("pretty_name", str), ("run", typing.Callable)])

excursion = _Test(0, "excursion", "5.1.1 Excursion Test Statistic", _excursion)
n_directional_runs = _Test(1, "n_directional_runs", "5.1.2 Number of Directional Runs", _n_directional_runs)
l_directional_runs = _Test(2, "l_directional_runs", "5.1.3 Length of Directional Runs", _l_directional_runs)
n_increases_decreases = _Test(
    3, "n_increases_decreases", "5.1.4 Number of Increases and Decreases", _n_increases_decreases
)
n_median_runs = _Test(4, "n_median_runs", "5.1.5 Number of Runs Based on the Median", _n_median_runs)
l_median_runs = _Test(5, "l_median_runs", "5.1.6 Length of Runs Based on Median", _l_median_runs)
avg_collision = _Test(6, "avg_collision", "5.1.7 Average Collision Test Statistic", _avg_collision)
max_collision = _Test(7, "max_collision", "5.1.8 Maximum Collision Test Statistic", _max_collision)
periodicity = _Test(8, "periodicity", "5.1.9 Periodicity Test Statistic", _periodicity)
covariance = _Test(9, "covariance", "5.1.10 Covariance Test Statistic", _covariance)
compression = _Test(10, "compression", "5.1.11 Compression Test Statistic", _compression)
tests = [
    excursion,
    n_directional_runs,
    l_directional_runs,
    n_increases_decreases,
    n_median_runs,
    l_median_runs,
    avg_collision,
    max_collision,
    periodicity,
    covariance,
    compression,
]


def run_tests(S, p, test_list=[i.id for i in tests]):
    """Run tests on a specified sequence, using a specified p value.
    If no tests are specified, all tests are run.

    Parameters
    ----------
    S : list of int
        sequence of sample values

    p : list of int
        list of p values

    test_list : list of int
        list of test indexes to run

    Returns
    -------
    list of float
        list of tests results
    """
    T = []
    for test_index in test_list:
        if test_index in [8, 9]:
            for p_value in p:
                result = tests[test_index].run(S, p_value)
                T.append(result)
        else:
            result = tests[test_index].run(S)
            T.append(result)
    return T


def calculate_counters(Tx, Ti):
    """Compute the counters C0 and C1 for the selected tests based on the condition provided by NIST. For each of the
    latter a given reference value Tx and a given list of values Ti is given: for each element of Ti, C0 is incremented
    if the latter is bigger than that Tx, C1 is incremented if they are equal.

    Parameters
    ----------
    Tx : list of float
        reference test values
    Ti : list of lists of float
        test values calculated on shuffled sequences

    Returns
    -------
    list of int, list of int
        list of counters C0, list of counters C1
    """

    C0 = [0 for k in range(len(Tx))]
    C1 = [0 for k in range(len(Tx))]

    for u in range(len(Tx)):
        for t in range(len(Ti)):
            if Tx[u] > Ti[t][u]:
                C0[u] += 1
            if Tx[u] == Ti[t][u]:
                C1[u] += 1

    return C0, C1


def iid_result(C0: list[int], C1: list[int], n_sequences: int):
    """Determine whether the sequence is IID by checking that the value of the reference result Tx is between 0.05% and
    99.95% of the results Ti for the rest of the population of n_sequences sequences.

    Parameters
    ----------
    C0 : list of int
        counter 0
    C1 : list of int
        counter 1
    n_sequences : int
        number of sequences in the population

    Returns
    -------
    bool
        iid result
    """
    if len(C0) != len(C1):
        raise Exception(f"Counter lengths must match: C0 ({len(C0)}), C1 ({len(C1)})")
    for b in range(len(C0)):
        if (C0[b] + C1[b] <= 0.0005 * n_sequences) or (C0[b] >= 0.9995 * n_sequences):
            return False
    return True


def FY_test_mode_parallel(S: list[int], n_permutations: int, selected_tests: list[int], p: list[int]):
    """Executes NIST test suite on shuffled sequence in parallel along n_permutations iterations

    Parameters
    ----------
    S : list of int
        sequence of sample values
    n_permutations: int
    selected_tests : list of
    p : list of int

    Returns
    -------
    list of float
        list of test outputs
    """
    Ti = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for iteration in range(n_permutations):
            s_shuffled = permutation_tests.FY_shuffle(S.copy())
            future = executor.submit(
                permutation_tests.run_tests,
                s_shuffled,
                p,
                selected_tests,
            )
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
