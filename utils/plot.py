import math
import os
import matplotlib.pyplot as plt
import numpy as np
import datetime
import pandas as pd
from datetime import datetime
from utils.useful_functions import get_next_run_number
from utils.config import test, distribution_test_index, n_sequences_stat, n_symbols, n_sequences


########################################################################
#########         DISTRIBUTION FUNCTIONS FOR NIST              #########
########################################################################


def histogram_TxTi(Tx, Ti, t, plot_dir_h):
    """Plots tests values in an histogram (with binning made such that bins are centered on an integer) 
    with the red vertical line as the reference value Tx.

    Parameters
    ----------
    Tx : list of float 
        Tx test values calculated on one sequence
    Ti : list of float
        Ti test values calculated on the shuffled sequences
    t : str
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
    ax.set_title(f"Distribution of the Results T for {t} test", size=12)
    ax.set_xlabel("T Values", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)

    # Displaying the legend
    ax.legend()

    plot_filename = f"{t.replace(' ', '_')}.png"
    plot_path = os.path.join(plot_dir_h, plot_filename)

    plt.savefig(plot_path)
    plt.show()
    plt.close()


def scatterplot_TxTi(Tx, Ti, t, plot_dir_s):
    """Plots tests values in a scatter plot with one dot for each observation of every shuffled sequence 
    and a red line for the reference Tx value

    Parameters
    ----------
    Tx : list of float 
        Tx test values calculated on one sequence
    Ti : list of float
        Ti test values calculated on the shuffled sequences
    t : str
        test executed
    plot_dir_s : str
        directory where to save the plot
    """
    x = [k for k in range(n_sequences)]

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.scatter(x, Ti, s=10)
    plt.xticks(np.arange(0, n_sequences, n_sequences / 10))
    # plt.yticks(np.arange(min(Ti) - 1, max(Ti) + 1, max(Ti) / config.n_sequences))
    plt.axhline(y=Tx, color="r", linestyle="-", label="axvline - full height")
    ax.text(Tx, 0.5, f"Tx={Tx}")

    my_text = rf"n_simbols={n_symbols}" + "\n" + rf"n_iterations={n_sequences}" + "\n" + rf"Tx={Tx}"
    props = dict(boxstyle="square", facecolor="grey", alpha=0.15)  # bbox features
    ax.text(0.93, 1.13, my_text, transform=ax.transAxes, fontsize=12, verticalalignment="top", bbox=props)

    plt.subplots_adjust(left=0.1)
    plt.title(t)

    plot_filename = f"{t.replace(' ', '_')}.png"
    plot_path = os.path.join(plot_dir_s, plot_filename)

    plt.savefig(plot_path)
    plt.show()
    plt.close()  # Close the plot without showing it


########################################################################
#########           DISTRIBUTION FUNCTION TO COMPARE          ##########
########################################################################


# Scatterplot random vs FY
def scatterplot_RvsFY(test, C0r, C0fy):
    """Plots the graph that compares the distribution of counters C0 computed considering sequences read from file with 
    the one obtained through FY shuffling.
    For each test, the mean value of C0 is represented as a dot with error bars and one standard deviation long.
    The two sets of results (random and shuffled) should overlap, hinting towards the IID hypotesis.
    The function computes the mean and std for each list making up C0r and C0fy and uses the results for the plot.


    Parameters
    ----------
    test : str
        test executed
    C0r : list of lists of int
        list containing the values of counters C0 using sequences read from file
    C0fy : list of lists of int
        list containing the results of counters C0 using FY shuffled sequence
    """
    data_1 = [np.mean(i) for i in C0r]
    err_1 = [np.std(i) for i in C0r]

    data_2 = [np.mean(i) for i in C0fy]
    err_2 = [np.std(i) for i in C0fy]

    fig, ax = plt.subplots()

    ax.errorbar(test, data_1, err_1, fmt="o", capsize=3, label="randomized sequences")
    ax.errorbar(test, data_2, err_2, fmt="o", capsize=3, label="shuffled FY sequences")
    plt.xlabel("Test")
    plt.ylabel("Values of the counter C0")
    ax.set_title("Comparison of the counters C0 for the randomized vs shuffled sequences", size=11)

    plt.legend()
    plt.show()
    plt.close()


def scatterplot_RvsFY_TjNorm(test, C0r, C0fy):
    """
    Plots the graph that compares the distribution of counters C0 computed considering sequences read from file with 
    the one obtained through FY shuffling.
    Modified version for TjNorm: adds a reference dashed orizontal line in n_sequences/4

    Parameters
    ----------
    test : str
        test executed
    C0r : list of lists of int
        list containing the values of counters C0 using sequences read from file
    C0fy : list of lists of int
        list containing the results of counters C0 using FY shuffled sequence
    """
    data_1 = [np.mean(i) for i in C0r]
    err_1 = [np.std(i) for i in C0r]

    data_2 = [np.mean(i) for i in C0fy]
    err_2 = [np.std(i) for i in C0fy]

    fig, ax = plt.subplots()
    ax.errorbar(test, data_1, err_1, fmt="o", capsize=3, label="randomized sequences")
    ax.errorbar(test, data_2, err_2, fmt="o", capsize=3, label="shuffled FY sequences")
    ax.axhline(n_sequences_stat / 4, color="red", linestyle="dashed")
    plt.xlabel("Test")
    plt.ylabel("Values of the counter C0")
    ax.set_title("Comparison of the counters C0 for the randomized vs shuffled sequences", size=11)

    plt.legend()
    plt.show()


########################################################################
#########                 COUNTERS DISTRIBUTION                #########
########################################################################

# 2) n_iteration_counter, n_sequences; used to compute the theoretical values of the binomial reference distribution.
# 3) test conducted
# These functions plot a histogram of distribution of the counter C0 for a given test.
# It plots the reference distribution and results and displays on the graph the measured mean and standard
# deviation of the set, the computed probability for the counter to be increased p ( based on the reference value for T)
# and the chi square for the assuming as null hypotesis a
# binomial distribution with parameters p and n_sequences. When changing the test one needs to change its name in the
# title at line 37. To get a better binning one can change the thid parameter in line 27: 1 means a bin for each
# integer, increasing it means merging more integers into one bin. For n_sequences=100 (or 200 in Tj) 3 is a nice
# choice. The choice of binning also influences the value of chi square.


def binomial_function(n, v, p):
    """Calculates the binomial distribution for a given  

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


def counters_distribution(c, n_seq, n_iter, t):
    """Plots a histogram of distribution of the counter C0 for a given test with the measured mean 
    and standard deviation

    Parameters
    ----------
    c : list of int
        counter values
    n_seq : int
        number of sequences
    n_iter : int
        number of iterations
    t : str
        test executed
    """
    # calculate the parameters of the distribution
    p = sum(c) / ((n_seq * n_iter))
    mean_teor = n_seq * p
    std_teor = np.sqrt(n_seq * p * (1 - p))

    # create histo of results to extract binning
    fig, ax = plt.subplots()

    bin_edges = np.arange(min(c) - 0.5, max(c) + 2.5, 3)
    bin_val, bin_edg, patches = ax.hist(c, bins=bin_edges, color="skyblue", edgecolor="black")
    fig.clf()
    plt.close()

    # calculate and plot reference binomial distribution
    fig, ax = plt.subplots()
    x_exp = np.arange(min(c), max(c) + 1, 1)
    y_exp = []
    for i in x_exp:
        y = n_iter * binomial_function(n_seq, i, p)
        y_exp.append(y)
    exp_val = [sum(y_exp[i : i + 3]) for i in range(0, len(y_exp), 3)]
    ax.stairs(exp_val, bin_edg, color="red", label="binomial fit")

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

    # plot results
    bin_center = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_err = [(np.sqrt(n * (1 - (n / n_iter)))) for n in bin_val]
    ax.errorbar(bin_center, bin_val, bin_err, fmt="o", color="blue", capsize=3, label="Data")

    textstr = "\n".join(
        (
            r"$mean=%.2f$" % (np.mean(c),),
            r"$std=%.2f$" % (np.std(c),),
            r"$p=%.2f$" % (p,),
            r"$\chi/ndf=%.2f$" % (chi_square_red,),
        )
    )
    props = dict(boxstyle="round", facecolor="w", alpha=0.5)
    ax.text(0.73, 0.90, textstr, transform=ax.transAxes, fontsize=14, verticalalignment="top", bbox=props)

    ax.set_title(f"Distribution {t} of the counter C0 for test {test}", size=14)
    plt.legend()
    plt.show()


def counters_distribution_Tx(c, n_seq, n_iter, t):
    """Plots a histogram of distribution of the counter C0 for a given test with the measured mean 
    and standard deviation

    Parameters
    ----------
    c : list of int
        counter values
    n_seq : int
        number of sequences
    n_iter : int
        number of iterations
    t : str
        test executed
    """
    # Calculate the parameters of the distribution
    p = sum(c) / (n_seq * n_iter)  # Calculate the success probability
    mean_teor = n_seq * p  # Theoretical mean
    std_teor = np.sqrt(n_seq * p * (1 - p))  # Theoretical standard deviation

    # Histogram of results to extract binning
    bin_edges = np.arange(min(c) - 0.5, max(c) + 2.5, 3)
    _, bin_edges = np.histogram(c, bins=bin_edges)
    bin_val, _, _ = plt.hist(c, bins=bin_edges, color="skyblue", edgecolor="black")
    plt.close()  # Close the plot as it's no longer needed

    # Calculate reference binomial distribution
    x_exp = np.arange(min(c), max(c) + 1, 1)
    y_exp = [n_iter * binomial_function(n_seq, i, p) for i in x_exp]
    exp_val = [sum(y_exp[i : i + 3]) for i in range(0, len(y_exp), 3)]

    # Prepare adjusted edges for ax.stairs, considering aggregation
    adjusted_edges = np.linspace(min(c) - 0.5, max(c) + 1.5, len(exp_val) + 1)

    fig, ax = plt.subplots()
    ax.stairs(exp_val, adjusted_edges, color="red", label="Binomial fit")

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

    # Calculate chi square
    """chi_square = sum(((bin_val[i] - exp_val[i]) ** 2 / exp_val[i]) for i in range(len(bin_val)) if exp_val[i] > 5)
    ndf = len([val for val in exp_val if val > 5])
    chi_square_red = chi_square / ndf if ndf else 0"""  # Avoid division by zero

    # Plot results with error bars
    bin_center = (adjusted_edges[:-1] + adjusted_edges[1:]) / 2
    bin_err = [np.sqrt(n * (1 - (n / n_iter))) for n in bin_val]
    ax.errorbar(bin_center[: len(bin_val)], bin_val, yerr=bin_err, fmt="o", color="blue", capsize=3, label="Data")

    # Text box for mean, std on the left
    textstr = "\n".join(
        (f"$mean={np.mean(c):.2f}$", f"$std={np.std(c):.2f}$", f"p={p:.3f}$", f"$\chi^2/ndf={chi_square_red:.2f}$")
    )
    props = dict(boxstyle="round", facecolor="w", alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10, verticalalignment="top", bbox=props)

    # Setting title and positioning the legend
    ax.set_title(f"Distribution {t} of the counter for test {test}", size=14)
    plt.legend(loc="upper right")
    plt.show()


def counters_distribution_Tj(c, n_seq, n_iter, t):
    """Plots a histogram of distribution of the counter C0 for a given test adjuested for Tj normalized

    Parameters
    ----------
    c : list of int
        counter values
    n_seq : int
        number of sequences
    n_iter : int
        number of iterations
    t : str
        test executed
    """
    # calculate the parameters of the distribution
    p = 0.5
    n_seq_norm = n_seq / 2
    mean_teor = n_seq_norm * p
    std_teor = np.sqrt(n_seq_norm * p * (1 - p))

    # create histo of results to extract binning
    fig, ax = plt.subplots()
    bin_edges = np.arange(min(c) - 0.5, max(c) + 2.5, 3)
    bin_val, bin_edges, patches = ax.hist(c, bins=bin_edges, color="skyblue", edgecolor="black")
    plt.close(fig)  # Close this plot as we only needed the binning information

    # Calculate and plot reference binomial distribution
    x_exp = np.arange(min(c), max(c) + 1, 1)
    y_exp = [n_iter * binomial_function(int(n_seq_norm), i, p) for i in x_exp]
    exp_val = [sum(y_exp[i : i + 3]) for i in range(0, len(y_exp), 3)]

    # Prepare the edges for the aggregated exp_val, ensuring the correct length
    new_edges = np.linspace(min(c) - 0.5, max(c) + 1.5, len(exp_val) + 1)

    # Replot with adjusted binning
    fig, ax = plt.subplots()
    ax.stairs(exp_val, new_edges, color="red", label="Binomial fit")

    # Adjust bin_center for error bars, ensuring they correspond to new_edges
    bin_center = (new_edges[:-1] + new_edges[1:]) / 2

    # Assuming bin_err calculation; adjust as necessary
    bin_err = [np.sqrt(val) for val in bin_val]  # Example adjustment; use appropriate calculation

    # Ensure bin_val is adjusted if necessary; here we're plotting as-is
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

    # Customize plot with additional information
    textstr = "\n".join(
        (f"$mean={mean_teor:.2f}$", f"$std={std_teor:.2f}$", f"p={p}$", f"$\chi^2/ndf={chi_square_red:.2f}$")
    )
    props = dict(boxstyle="round", facecolor="w", alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14, verticalalignment="top", bbox=props)

    ax.set_title(f"Distribution {t} of the counter for test {test}", size=14)
    plt.legend()
    plt.show()


def counters_distribution_file_plot(f, n_symbols, n_sequences, n_iterations_c):
    """Plots a histogram of distribution of the counter C0 read from file with the measured mean 
    and standard deviation

    Parameters
    ----------
    f : str
        path to file
    n_symbols : int
        number of symbols
    n_sequences : int
        number of sequences
    n_iterations_c : int
        number of iterations
    """
    df = pd.read_csv(f)
    d = df["COUNTER_0"][0]
    list_elements = d[1:-1].split(",")

    # Convert the string elements to integers
    c = [int(element) for element in list_elements]
    # print(c)

    fig, ax = plt.subplots(figsize=(15, 6))

    bin_edges = np.arange(min(c) - 0.5, max(c) + 1.5, 1)
    ax.hist(c, bins=bin_edges, edgecolor="black")
    plt.xticks(np.arange(min(c), max(c) + 1))

    my_text = "Parameters used\n"
    my_text += (
        rf"n_simbols={n_symbols}"
        + "\n"
        + rf"n_sequences={n_sequences}"
        + "\n"
        + rf"n_counters={n_iterations_c}"
        + "\n"
        + rf"test={test}"
        + "\n"
        + rf'date={datetime.date.today().strftime("%d/%m/%Y")}'
        + rf"x_range=[{min(c)}] - [{max(c)}]"
    )
    props = dict(boxstyle="square", facecolor="grey", alpha=0.15)  # bbox features
    ax.text(0.85, 0.99, my_text, transform=ax.transAxes, fontsize=12, verticalalignment="top", bbox=props)
    plt.tight_layout()
    plt.show()

    def get_sixth_feature_last_series_first_element(file_path):
        # Load the CSV file into a pandas DataFrame
        data = pd.read_csv(file_path)

        # Extract the sixth feature (column) assuming the first column is at index 0
        sixth_feature = data.iloc[:, 5]  # Adjust the index if needed

        # Extract the last entry in the sixth column
        last_entry = sixth_feature.iloc[-1]

        # Assuming the last entry is a string representation of a list, convert it to a list
        # Note: This step might need adjustment based on the actual content/format of your CSV
        last_entry_as_list = eval(last_entry)

        # Return the first element of this list
        return last_entry_as_list

    """file_path = '/architecture/results/counters_distribution/FYShuffleTx/fyShuffleTx_n_directional_runs.csv'  # Update this path to your actual file path
    first_element_of_last_series = get_sixth_feature_last_series_first_element(file_path)
    print(first_element_of_last_series)"""
