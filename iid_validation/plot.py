import math
import os
import statistics

import matplotlib.pyplot as plt
import numpy as np

from . import permutation_tests


def histogram_TxTi(Tx: float, Ti: list[float], test_label: str, test_isint: bool, plot_dir_h: str) -> None:
    """Plots tests values in an histogram (with binning made such that bins are centered on an integer)
    with the red vertical line as the reference value Tx.

    Parameters
    ----------
    Tx : float
        Tx test values calculated on one sequence
    Ti : list of float
        Ti test values calculated on the shuffled sequences
    test_label : str
        test executed
    test_isint: bool
        True if the test executed returns an int
    plot_dir_h : str
        directory where to save the plot
    """
    fig, ax = plt.subplots()

    # Creating bins for histogram
    n_bins = 30
    bin_width = (-min(Ti) + 0.5 + max(Ti) + 1.5) / n_bins
    # if the data is int, consider an integer number of values for each bin to avoid binning artifacts
    if test_isint:
        bin_width = math.ceil(bin_width)
    bin_edges = list(np.arange(min(Ti) - 0.5, max(Ti) + 1.5, bin_width))
    # as np.arange considers an half open interval [start, stop), check if the last bin edge covers the maximum of Ti
    # and add another bin edge to the right if necessary
    if bin_edges[-1] < max(Ti):
        bin_edges.append(bin_edges[-1] + bin_width)
    # Plotting histogram for Ti
    ax.hist(Ti, bins=bin_edges, color="skyblue", edgecolor="black")
    # Adding a vertical line for Tx
    reference_label = "Reference Value: " + (f"{Tx}" if test_isint else f"{Tx:.2f}")
    ax.axvline(x=Tx, color="red", label=reference_label)

    # Preparing text string for mean and std
    textstr = rf"""$\mu={statistics.mean(Ti):.2f}$
$\sigma={statistics.stdev(Ti):.2f}$"""

    # Text box properties
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    # Placing text box on the plot
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12, verticalalignment="top", bbox=props)

    # Setting title and axis labels
    ax.set_title(f"Distribution of the Results T for {test_label} test", size=12)
    ax.set_xlabel("T Values", fontsize=12)
    ax.set_ylabel("Occurrencies", fontsize=12)

    # Displaying the legend
    ax.legend(loc="upper right")

    plot_filename = f"{test_label}.pdf"
    plot_path = os.path.join(plot_dir_h, plot_filename)

    plt.savefig(plot_path)
    plt.close()


def binomial_function(n: int, v: int, p: float) -> float:
    """Calculates the binomial distribution for a given set of parameters.

    Parameters
    ----------
    n : int
        number of trials
    v : int
        number of successes in trial
    p : float
        probability of a single success

    Returns
    -------
    float
        binomial distribution value
    """
    f = (math.factorial(n) / (math.factorial(v) * math.factorial(n - v))) * (p**v) * (1 - p) ** (n - v)
    return f


def counters_distribution(c: list[int], n_seq: int, n_iter: int, test: int, method: str) -> None:
    """Plots a histogram of the distribution of the counter C0 for a given test with the measured mean and
    standard deviation.

    Parameters
    ----------
    c : list of int
        counter values
    n_seq : int
        number of sequences
    n_iter : int
        number of iterations
    test : int
        index of the executed permutation test
    method : str
        method of computation of the counter
    """
    # Calculate the parameters of the distribution
    # if the counters are computed with the Tj method, the sequences are considered in pairs and discarded if they give
    # the same result under the test considered. In this case the probability of updating the counter is 50% and the
    # number of effective sequences is halved
    if method == "Tj":
        p = 0.5
        n_seq = int(n_seq / 2)
    # else, i.e. with the Tx method, the probability of updating a counter depends on the reference value Tx and is
    # therefore computed empirically as the fraction of the Ti which are smaller than Tx
    else:
        p = sum(c) / (n_seq * n_iter)

    # Histogram of results to extract binning
    n_bins = 10
    bin_width = math.ceil((-min(c) + 0.5 + max(c) + 1.5) / n_bins)
    bin_edges = list(np.arange(min(c) - 0.5, max(c) + 1.5, bin_width))
    # as np.arange considers an half open interval [start, stop), check if the last bin edge covers the maximum of Ti
    # and add another bin edge to the right if necessary
    if bin_edges[-1] < max(c):
        bin_edges.append(bin_edges[-1] + bin_width)
    bin_val, _, _ = plt.hist(c, bins=bin_edges, color="skyblue", edgecolor="black")

    plt.close()

    # Calculate reference binomial distribution
    x_exp = np.arange(bin_edges[0] + 0.5, bin_edges[-1] + 0.5, 1)

    y_exp = [n_iter * binomial_function(n_seq, int(i), p) if i <= n_seq else 0 for i in x_exp]
    exp_val = [sum(y_exp[i : i + bin_width]) for i in range(0, len(y_exp), bin_width)]

    fig, ax = plt.subplots()
    ax.stairs(exp_val, bin_edges, color="red", label="Binomial fit")

    # compute chi square
    chi_square = 0
    ndf = 0
    for i in range(len(bin_val)):
        if exp_val[i] != 0:
            chi_square += (bin_val[i] - exp_val[i]) ** 2 / exp_val[i]
            ndf += 1
    chi_square_red = chi_square / ndf

    # Plot results with error bars
    bin_center = [(bin_edges[i] + bin_edges[i + 1]) / 2 for i in range(len(bin_edges) - 1)]
    bin_err = [math.sqrt(n * (1 - (n / n_iter))) for n in bin_val]
    ax.errorbar(bin_center, bin_val, yerr=bin_err, fmt="o", color="blue", capsize=3, label="Data")

    # Text box for mean, std on the left
    textstr = rf"""$mean={statistics.mean(c):.2f}$
$std={statistics.stdev(c):.2f}$
p={p:.3f}
$\chi^2/ndf={chi_square_red:.2f}$"""

    props = dict(boxstyle="round", facecolor="w", alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10, verticalalignment="top", bbox=props)

    # Setting title and positioning the legend
    ax.set_title(f"Distribution of C0 for test {permutation_tests.tests[test].name}, {method} method", size=14)
    plt.legend(loc="upper right")

    # Define and create the directory
    directory_path = os.path.join(f"counters{method}_distribution")
    os.makedirs(directory_path, exist_ok=True)

    plot_filename = f"counters{method}_{permutation_tests.tests[test].name}.pdf"
    plot_path = os.path.join(directory_path, plot_filename)

    plt.savefig(plot_path)
    plt.close()


def min_entropy(
    symbols_occ: dict[int, int],
    frequencies: list[float],
    n_symbols: int,
    H_min: float,
    H_min_sigma: float,
    H_min_NIST: float,
):
    """Plot of the frequencies of the symbols

    Parameters
    ----------
    symbols_occ : dict of int, int
        occurrences of the symbols
    frequencies : list of float
        frequencies of the symbols
    n_symbols: int
        total number of symbols
    H_min : float
        min-entropy
    H_min_sigma: float
        error on min-entropy
    H_min_NIST : float
        NIST min-entropy
    """
    # binomial error on frequencies
    err_y = []
    for x in symbols_occ:
        a = symbols_occ[x] * (1 - (symbols_occ[x] / n_symbols))
        err_y.append(math.sqrt(a) / n_symbols)

    # plot frequencies
    fig, ax = plt.subplots()
    ax.errorbar(symbols_occ.keys(), frequencies, err_y, fmt="o", capsize=3)
    ax.axhline(1 / 16, 0, 1, label="uniform distribution", color="red", linestyle="dashed")
    plt.suptitle("Min-Entropy and Symbol Distribution")
    textstr = rf"""$H_{{min}}={H_min:.4f}\pm{H_min_sigma:.4f}$, $H_{{min}}$ NIST={H_min_NIST:.4f}"""
    plt.title(textstr, fontsize=10)
    plt.xticks([i for i in range(16)], size=12)

    ax.set_xlabel("Symbols")
    ax.set_ylabel("Frequency of the symbols")

    plt.legend(loc="lower right", fancybox=True, framealpha=1)
    plt.savefig("MinEntropy.pdf", bbox_inches="tight")
    plt.close()
