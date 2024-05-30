import bz2
import concurrent.futures
import random
import statistics
import sys
import typing

from tqdm import tqdm


def FY_shuffle(S: list[int]) -> list[int]:
    """Generates a shuffled sequence using the Fisher-Yates algorithm.

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


def s_prime(S: list[int]) -> list[int]:
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


def s_prime_median(S: list[int], M: float | None = None) -> list[int]:
    """Generates a transformed sequence where each original value is replaced with -1 if it is less than the median of
    the original sequence, or 1 if it is greater than or equal to the median.

    Accepts a pre-computed median value, if provided.

    Parameters
    ----------
    S : list of int
        sequence of sample values
    M: float
        the pre-computed median of the sequence

    Returns
    -------
    list of int
        new sequence of -1s and +1s
    """
    if len(S) == 0:
        raise Exception("Input sequence has length 0")

    if M is None:
        M = statistics.median(S)

    S_prime = [0] * (len(S))
    for i in range(len(S)):
        if S[i] < M:
            S_prime[i] = -1
        else:
            S_prime[i] = 1
    return S_prime


def compute_collisions(S: list[int]) -> list[int]:
    """Counts the number of successive sample values until a duplicate is found.

    Parameters
    ----------
    S : list[int]
        sequence of sample values

    Returns
    -------
    list[int]
        list of the numbers of samples observed to find a duplicate in the input sequence
    """
    seen = set()
    C = []
    last_split = 0
    for i, x in enumerate(S, 1):
        if x in seen:
            C.append(i - last_split)
            last_split = i
            seen.clear()
        else:
            seen.add(x)
    return C


def n_runs(S_prime: list[int]) -> int:
    """Determines the number of runs of identical symbols in a sequence.

    Assumes a sequence of length > 0.

    Parameters
    ----------
    S_prime : list of int
        an input sequence processed with s_prime() or s_prime_median()

    Returns
    -------
    int
        number of runs in the sequence
    """
    T = 1
    for i in range(1, len(S_prime)):
        if S_prime[i] != S_prime[i - 1]:
            T += 1
    return T


def l_runs(S_prime: list[int]) -> int:
    """Determines the length of the longest run of identical symbols in a sequence.

    Assumes a sequence of length > 0.

    Parameters
    ----------
    S_prime : list of int
        an input sequence processed with s_prime() or s_prime_median()

    Returns
    -------
    int
        length of the longest run in the sequence
    """
    T = 0
    current_len = 1

    for i in range(1, len(S_prime)):
        if S_prime[i] == S_prime[i - 1]:
            current_len += 1
        else:
            if current_len > T:
                T = current_len
            current_len = 1
    # Measure last run
    if current_len > T:
        T = current_len

    return T


def _excursion(S: list[int], X: float | None = None) -> float:
    """Measures how far the running sum of sample values deviates from its average value at each point in the sequence.

    Accepts a pre-computed average value, if provided.

    Parameters
    ----------
    S : list of int
        sequence of sample values
    X : float
        the pre-computed average of the sequence

    Returns
    -------
    float
        maximum deviation from the average
    """
    if X is None:
        X = statistics.mean(S)

    cumulative_sum = 0
    D = [abs((cumulative_sum := cumulative_sum + element) - (i * X)) for i, element in enumerate(S, 1)]  # noqa: F841
    return max(D)


def _n_directional_runs(S: list[int], S_prime: list[int] | None = None) -> int:
    """Measures the number of runs constructed using the relations between consecutive samples.

    Accepts a pre-computed S_prime sequence, if provided.

    Parameters
    ----------
    S : list of int
        sequence of sample values
    S_prime: list of int
        the pre-computed s_prime(S) sequence

    Returns
    -------
    int
        number of runs
    """
    if S_prime is None:
        S_prime = s_prime(S)

    return n_runs(S_prime)


def _l_directional_runs(S: list[int], S_prime: list[int] | None = None) -> int:
    """Measures the length of the longest run constructed using the relations between consecutive samples.

    Accepts a pre-computed S_prime sequence, if provided.

    Parameters
    ----------
    S : list of int
        sequence of sample values
    S_prime: list of int
        the pre-computed s_prime(S) sequence

    Returns
    -------
    int
        length of the longest run of consecutive samples that are either strictly increasing or strictly decreasing
    """
    if S_prime is None:
        S_prime = s_prime(S)

    return l_runs(S_prime)


def _n_increases_decreases(S: list[int], S_prime: list[int] | None = None) -> int:
    """Measures the maximum number of increases or decreases between consecutive sample values.

    Accepts a pre-computed S_prime sequence, if provided.

    Parameters
    ----------
    S : list of int
        sequence of sample values
    S_prime: list of int
        the pre-computed s_prime(S) sequence

    Returns
    -------
    int
        greater number between the total counts of increases and decreases among consecutive sample values
    """
    if S_prime is None:
        S_prime = s_prime(S)

    count = S_prime.count(1)

    return max(count, len(S_prime) - count)


def _n_median_runs(S: list[int], S_prime_median: list[int] | None = None) -> int:
    """Measures the number of runs that are constructed with respect to the median of the sequence.

    Accepts a pre-computed S_prime_median sequence, if provided.

    Parameters
    ----------
    S : list of int
        sequence of sample values
    S_prime_median: list of int
        the pre-computed s_prime_median(S) sequence

    Returns
    -------
    int
        number of runs
    """
    if S_prime_median is None:
        S_prime_median = s_prime_median(S)

    return n_runs(S_prime_median)


def _l_median_runs(S: list[int], S_prime_median: list[int] | None = None) -> int:
    """Measures the length of the longest run constructed with respect to the median of the sequence.

    Accepts a pre-computed S_prime_median sequence, if provided.

    Parameters
    ----------
    S : list of int
        sequence of sample values
    S_prime_median: list of int
        the pre-computed s_prime_median(S) sequence

    Returns
    -------
    int
        length of the longest run
    """
    if S_prime_median is None:
        S_prime_median = s_prime_median(S)

    return l_runs(S_prime_median)


def _avg_collision(S: list[int], C: list[int] | None = None) -> float:
    """Counts the number of successive sample values until a duplicate is found.

    Accepts a pre-computed list of collisions C calculated on the sequence S, if provided.

    Parameters
    ----------
    S : list of int
        sequence of sample values
    C: list of int
        list of number of samples observed to find two occurrences of the same value in the input sequence

    Returns
    -------
    float
        average number of samples observed to find two occurrences of the same value in the input sequence
    """
    if C is None:
        C = compute_collisions(S)
    return statistics.mean(C)


def _max_collision(S: list[int], C: list[int] | None = None) -> int:
    """Counts the number of successive sample values until a duplicate is found.

    Accepts a pre-computed list of collisions C calculated on the sequence S, if provided.

    Parameters
    ----------
    S : list of int
        sequence of sample values
    C: list of int
        list of number of samples observed to find two occurrences of the same value in the input sequence

    Returns
    -------
    int
        maximum number of samples observed to find two occurrences of the same value in the input sequence
    """
    if C is None:
        C = compute_collisions(S)
    return max(C)


def _periodicity(S: list[int], p: int) -> int:
    """Determines the number of periodic samples in the sequence.

    Parameters
    ----------
    S : list of int
        sequence of sample values
    p : int
        lag parameter

    Returns
    -------
    int
        number of instances where an element in the sequence is equal to another element that is y positions ahead
    """
    T = 0
    for i in range(0, len(S) - p):
        if S[i] == S[i + p]:
            T += 1
    return T


def _covariance(S: list[int], p: int) -> int:
    """Measures the strength of the lagged correlation.

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


def _compression(S: list[int]) -> int:
    """Measures the length of the sequence encoded into a character string and processed by a general-purpose
    compression algorithm (bzip2).

    The sequence is encoded as a list of its values separated by a single space.

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
    # Select compresslevel=5 to make results numerically identical to NIST implementation
    t = bz2.compress(S_string.encode("utf-8"), compresslevel=5)
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


def run_tests(S: list[int], p: list[int], test_list: list[int] = [i.id for i in tests]) -> list[float]:
    """Runs a list of tests on a specified sequence, using a specified p value.
    By default, all tests are run.

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

    # Pre-compute common intermediate values
    S_prime = None
    if set((n_directional_runs.id, l_directional_runs.id, n_increases_decreases.id)).intersection(test_list):
        S_prime = s_prime(S)
    S_prime_median = None
    if set((n_median_runs.id, l_median_runs.id)).intersection(test_list):
        S_prime_median = s_prime_median(S)
    collisions = None
    if set((avg_collision.id, max_collision.id)).intersection(test_list):
        collisions = compute_collisions(S)

    if excursion.id in test_list:
        T.append(excursion.run(S))
    if n_directional_runs.id in test_list:
        T.append(n_directional_runs.run(S, S_prime))
    if l_directional_runs.id in test_list:
        T.append(l_directional_runs.run(S, S_prime))
    if n_increases_decreases.id in test_list:
        T.append(n_increases_decreases.run(S, S_prime))
    if n_median_runs.id in test_list:
        T.append(n_median_runs.run(S, S_prime_median))
    if l_median_runs.id in test_list:
        T.append(l_median_runs.run(S, S_prime_median))
    if avg_collision.id in test_list:
        T.append(avg_collision.run(S, collisions))
    if max_collision.id in test_list:
        T.append(max_collision.run(S, collisions))
    if periodicity.id in test_list:
        for each_p in p:
            T.append(periodicity.run(S, each_p))
    if covariance.id in test_list:
        for each_p in p:
            T.append(covariance.run(S, each_p))
    if compression.id in test_list:
        T.append(compression.run(S))

    return T


def calculate_counters(Tx: list[float], Ti: list[list[float]]) -> tuple[list[int], list[int]]:
    """Computes the counters C0 and C1 for the selected tests.

    For each test, the reference value Tx is compared to the list of values Ti: for each element of Ti, C0 is
    incremented if Ti is bigger than Tx, C1 is incremented if they are equal.

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

    C0 = [0] * len(Tx)
    C1 = [0] * len(Tx)

    for u in range(len(Tx)):
        for t in range(len(Ti)):
            if Tx[u] > Ti[t][u]:
                C0[u] += 1
            if Tx[u] == Ti[t][u]:
                C1[u] += 1

    return C0, C1


def iid_result(C0: list[int], C1: list[int], n_permutations: int) -> bool:
    """Determines whether the sequence is IID by checking that the value of the reference result Tx is between 0.05% and
    99.95% of the results Ti for the rest of the population of n_permutations sequences.

    Parameters
    ----------
    C0 : list of int
        counter 0
    C1 : list of int
        counter 1
    n_permutations : int
        number of sequences in the population

    Returns
    -------
    bool
        iid result
    """
    if len(C0) != len(C1):
        raise Exception(f"Counter lengths must match: C0 ({len(C0)}), C1 ({len(C1)})")
    for b in range(len(C0)):
        if (C0[b] + C1[b] <= 0.0005 * n_permutations) or (C0[b] >= 0.9995 * n_permutations):
            return False
    return True


def run_tests_permutations(
    S: list[int], n_permutations: int, selected_tests: list[int], p: list[int], parallel: bool = True
) -> list[list[float]]:
    """Executes the NIST test suite on n_permutations shuffled sequences.

    The sequences are tested in parallel depending on the parallel parameter (True by default).
    Parallelization is achieved by multiprocessing, with the number of parallel processes corresponding to the number of
    available processors.

    Parameters
    ----------
    S : list of int
        sequence of sample values
    n_permutations: int
        number of permutations
    selected_tests : list of int
        indexes of the selected tests
    p : list of int
        parameter p
    parallel: bool
        Test sequences in parallel or not

    Returns
    -------
    list of list of float
        list of test outputs
    """
    Ti = []

    if parallel:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []
            for _ in range(n_permutations):
                s_shuffled = FY_shuffle(S.copy())
                future = executor.submit(
                    run_tests,
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
    else:
        for _ in tqdm(range(n_permutations)):
            s_shuffled = FY_shuffle(S.copy())
            result = run_tests(s_shuffled, p, selected_tests)
            Ti.append(result)
    return Ti
