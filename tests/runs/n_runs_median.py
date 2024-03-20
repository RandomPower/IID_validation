""" 5.1.5 Number of Runs based on median"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
from architecture.utils.config import n_symbols, n_sequences


def statistic_n_median_runs(s_sequences):
    # compute the observable: number of runs based on the median for each S
    num_M_runs = []
    sprime_sequences = []
    for i in s_sequences:
        num_runs, S_prime = n_median_runs(i)
        num_M_runs.append(num_runs)
        sprime_sequences.append(S_prime)

    # compute the theoretical features of the distribution
    num_M_runs_mean = []
    for i in sprime_sequences:
        n_plus = i.count(1)
        frac = n_plus / n_symbols
        R_mean = 2 * n_symbols * frac * (1 - frac) + 1
        num_M_runs_mean.append(R_mean)

    num_M_runs_var = []
    for i in sprime_sequences:
        n_plus = i.count(1)
        frac = n_plus / n_symbols
        R_var = (n_symbols / (n_symbols - 1)) * (2 * frac * (1 - frac) * (2 * n_symbols * frac * (1 - frac) - 1))
        num_M_runs_var.append(R_var)

    # plot histogram of num_M_runs
    mean = np.mean(num_M_runs)
    std = np.std(num_M_runs)

    fig, ax = plt.subplots()
    bin_edges = np.arange(min(num_M_runs) - 0.5, max(num_M_runs) + 1.5, 1)
    ax.hist(num_M_runs, bin_edges, color="skyblue", edgecolor="black")
    textstr = "\n".join(
        (
            r"$mean=%.2f$" % (np.mean(num_M_runs),),
            r"$std=%.2f$" % (np.std(num_M_runs),),
        )
    )
    props = dict(boxstyle="round", facecolor="w", alpha=0.5)
    ax.text(0.15, 0.35, textstr, transform=ax.transAxes, fontsize=14, verticalalignment="top", bbox=props)
    plt.title("Distribution of the number of runs with respect to the median per sequence", size=14)
    plt.show()

    # compute z-score: with theoretical R_mean and R_var computed for each sequence
    Z = []
    for i in range(n_sequences):
        z = (num_M_runs[i] - num_M_runs_mean[i]) / np.sqrt(num_M_runs_var[i])
        Z.append(z)

    # plot histogram of z-score
    fig, ax = plt.subplots()
    LL = -9.5 * np.std(Z)
    UL = 9.5 * np.std(Z)
    bin_size = np.std(Z) / 9
    bins = np.linspace(LL, UL, num=int((UL - LL) / bin_size))
    bin_values, bin_edges, patches = ax.hist(Z, bins, color="skyblue", edgecolor="black")

    # gaussian fit
    def gauss(x, amp, mu, sigma):
        return amp * np.exp(-((x - mu) ** 2) / 2 * (sigma) ** 2)

    x = np.linspace(LL, UL, int((UL - LL) / bin_size) - 1)
    y = bin_values
    par_guess = [len(Z), np.mean(Z), np.std(Z)]

    par_opt, par_cov = opt.curve_fit(gauss, x, y, par_guess)
    par_err = np.sqrt(np.diag(par_cov))
    amp, mu, sigma = par_opt
    amp_err, mu_err, sigma_err = par_err

    x1 = np.linspace(LL, UL, 10000)
    ax.plot(x1, gauss(x1, *par_opt), color="red", label="fit")

    # plot costumization
    textstr = "\n".join((r"$mean=%.2f \pm%.2f$" % (mu, mu_err), r"$std=%.2f \pm%.2f$" % (sigma, sigma_err)))
    props = dict(boxstyle="round", facecolor="w", alpha=0.5)
    ax.text(0.15, 0.35, textstr, transform=ax.transAxes, fontsize=14, verticalalignment="top", bbox=props)

    ax.set_title("Distribution of the z-scores of the number of runs with respect to the median per sequence", size=14)

    plt.show()


def n_median_runs(S):
    X = np.median(S)
    S_prime = []
    for i in range(len(S)):
        if S[i] < X:  # PROBLEM: 7 = 7.0 GIVES +1
            S_prime.append(-1)
        else:
            S_prime.append(1)
    if len(S_prime) == 0:
        return 0
    # print(S_prime)

    T = 1
    for i in range(1, len(S_prime)):
        if S_prime[i] != S_prime[i - 1]:
            T += 1
    return T


"""S = (5, 15, 12_normal, 1, 13, 9, 4, 9, 20, 3, 1, 7, 8, 5, 2)
print(n_median_runs(S))"""
