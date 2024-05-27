import math
import os
import statistics

import matplotlib.pyplot as plt
import numpy as np

import permutation_tests


def histogram_TxTi(Tx, Ti, test_label, plot_dir_h):
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
    plot_dir_h : str
        directory where to save the plot
    """
    fig, ax = plt.subplots()

    # Creating bins for histogram
    bin_edges = np.arange(min(Ti) - 0.5, max(Ti) + 1.5, 3)
    # Plotting histogram for Ti
    ax.hist(Ti, bins=bin_edges, color="skyblue", edgecolor="black")
    # Adding a vertical line for Tx
    ax.axvline(x=Tx, color="red", label=f"Target Value: {Tx}")

    # Preparing text string for mean and std
    textstr = "\n".join((r"$\mu=%.2f$" % (np.mean(Ti),), r"$\sigma=%.2f$" % (np.std(Ti),)))
    # Text box properties
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    # Placing text box on the plot
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12, verticalalignment="top", bbox=props)

    # Setting title and axis labels
    ax.set_title(f"Distribution of the Results T for {test_label} test", size=12)
    ax.set_xlabel("T Values", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)

    # Displaying the legend
    ax.legend()

    plot_filename = f"{test_label}.pdf"
    plot_path = os.path.join(plot_dir_h, plot_filename)

    plt.savefig(plot_path)
    plt.close()


def binomial_function(n, v, p):
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


def counters_distribution_Tx(c, n_seq, n_iter, test):
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
    """
    # Calculate the parameters of the distribution
    p = sum(c) / (n_seq * n_iter)

    # Histogram of results to extract binning
    bin_edges = np.arange(min(c) - 0.5, max(c) + 2.5, 3)
    _, bin_edges = np.histogram(c, bins=bin_edges)
    bin_val, _, _ = plt.hist(c, bins=bin_edges, color="skyblue", edgecolor="black")
    plt.close()

    # Calculate reference binomial distribution
    x_exp = np.arange(min(c), max(c) + 1, 1)
    y_exp = [n_iter * binomial_function(n_seq, i, p) for i in x_exp]
    exp_val = [sum(y_exp[i : i + 3]) for i in range(0, len(y_exp), 3)]

    # Prepare adjusted edges for ax.stairs
    adjusted_edges = np.linspace(min(c) - 0.5, max(c) + 1.5, len(exp_val) + 1)

    fig, ax = plt.subplots()
    ax.stairs(exp_val, adjusted_edges, color="red", label="Binomial fit")

    # compute chi square
    chi_square = 0
    ndf = 0
    for i in range(len(bin_val)):
        if exp_val[i] < 0:
            continue
        else:
            chi_square += (bin_val[i] - exp_val[i]) ** 2 / exp_val[i]
            ndf += 1
    chi_square_red = chi_square / ndf

    # Plot results with error bars
    bin_center = (adjusted_edges[:-1] + adjusted_edges[1:]) / 2
    bin_err = [np.sqrt(n * (1 - (n / n_iter))) for n in bin_val]
    ax.errorbar(bin_center[: len(bin_val)], bin_val, yerr=bin_err, fmt="o", color="blue", capsize=3, label="Data")

    # Text box for mean, std on the left
    textstr = "\n".join(
        (f"$mean={np.mean(c):.2f}$", f"$std={np.std(c):.2f}$", f"p={p:.3f}", rf"$\chi^2/ndf={chi_square_red:.2f}$")
    )
    props = dict(boxstyle="round", facecolor="w", alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10, verticalalignment="top", bbox=props)

    # Setting title and positioning the legend
    ax.set_title(f"Distribution of C0 for test {permutation_tests.tests[test].name}, Tx method", size=14)
    plt.legend(loc="upper right")

    # Define and create the directory
    directory_path = os.path.join("countersTx_distribution")
    os.makedirs(directory_path, exist_ok=True)

    plot_filename = f"countersTx_{permutation_tests.tests[test].name}.pdf"
    plot_path = os.path.join(directory_path, plot_filename)

    plt.savefig(plot_path)
    plt.close()


def counters_distribution_Tj(c, n_seq, n_iter, test):
    """Plots a histogram of the distribution of the counter C0 for a given test adjusted for Tj normalized.

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
    t : str
        test executed
    plot_dir : str
        directory where to save the plot
    """
    # calculate the parameters of the distribution
    p = 0.5
    n_seq_norm = n_seq / 2

    # create histo of results to extract binning
    fig, ax = plt.subplots()
    bin_edges = np.arange(min(c) - 0.5, max(c) + 2.5, 3)
    bin_val, bin_edges, patches = ax.hist(c, bins=bin_edges, color="skyblue", edgecolor="black")
    plt.close(fig)

    # Calculate and plot reference binomial distribution
    x_exp = np.arange(min(c), max(c) + 1, 1)
    y_exp = [n_iter * binomial_function(int(n_seq_norm), i, p) for i in x_exp]
    exp_val = [sum(y_exp[i : i + 3]) for i in range(0, len(y_exp), 3)]

    # Prepare the edges for the aggregated exp_val
    new_edges = np.linspace(min(c) - 0.5, max(c) + 1.5, len(exp_val) + 1)

    # Replot with adjusted binning
    fig, ax = plt.subplots()
    ax.stairs(exp_val, new_edges, color="red", label="Binomial fit")

    # Adjust bin_center for error bars
    bin_center = (new_edges[:-1] + new_edges[1:]) / 2

    bin_err = [np.sqrt(n * (1 - (n / n_iter))) for n in bin_val]

    ax.errorbar(
        bin_center[: len(bin_val)],
        bin_val,
        yerr=bin_err[: len(bin_val)],
        fmt="o",
        color="blue",
        capsize=3,
        label="Data",
    )

    # calculate chi square
    chi_square = 0
    ndf = 0
    for i in range(len(bin_val)):
        if exp_val[i] < 0:
            continue
        else:
            chi_square += (bin_val[i] - exp_val[i]) ** 2 / exp_val[i]
            ndf += 1

    chi_square_red = chi_square / ndf

    # Box with parameters of the distribution
    textstr = "\n".join(
        (
            f"$mean={statistics.mean(c):.2f}$",
            f"$std={statistics.stdev(c):.2f}$",
            f"p={p}",
            rf"$\chi^2/ndf={chi_square_red:.2f}$",
        )
    )
    props = dict(boxstyle="round", facecolor="w", alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment="top", bbox=props)

    ax.set_title(f"Distribution of C0 for test {permutation_tests.tests[test].name}, TjNorm method", size=14)
    plt.legend()

    # Define and create the directory
    directory_path = os.path.join("countersTjNorm_distribution")
    os.makedirs(directory_path, exist_ok=True)

    plot_filename = f"countersTjNorm_{permutation_tests.tests[test].name}.pdf"
    plot_path = os.path.join(directory_path, plot_filename)

    plt.savefig(plot_path)
    plt.close()
