"""
CONFIGURATION FILE - CHANGE VARIABLES TO RUN THE DESIRED CONFIGURATION
"""

# GLOBAL VARIABLES
file = (
    "/Users/olivia1/Desktop/RANDOM POWER/project_entropy_validation/bits_RandomPower/test1"
    "/getbits_20230401_195315_RAW_BITS.BIN"
)
bool_test_NIST = True
bool_statistical_analysis = False

# NIST TEST VARIABLES
n_symbols = 1000
n_sequences = 100000
bool_shuffle_NIST = True  # --> if True: FY shuffle, if False: use random sampling from file
bool_first_seq = True  # --> if True: reference sequence read from beginning; if False: reference sequence from the end
bool_pvalue = False  # --> if True: NIST values, if False: user chooses value
see_plots = False

if bool_pvalue:
    p = [1, 2, 8, 16, 32]  # NIST values
else:
    p = 2  # User sets preferred value


# STATISTICAL ANALYSIS VARIABLES
n_sequences_stat = 200
n_symbols_stat = 1000
n_iterations_c_stat = 500  # counter distruibution iterations
distribution_test_index = 6  # Select which test index for counter distribution

bool_shuffle_stat = True  # --> if True: FY shuffle, if False: use random sampling from file

p_value_stat = 2  # User sets preferred value
ref_numbers = [1, 3, 4]  # Select which test indexes for shuffle/random comparison

# GLOBAL VARIABLES
test_list_indexes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Select which tests to test IID assumption
step = n_symbols / 2  # step in reading bin file

# Test list
test_list = {
    0: "excursion_test",
    1: "n_directional_runs",
    2: "l_directional_runs",
    3: "n_median_runs",
    4: "l_median_runs",
    5: "n_increases_decreases",
    6: "avg_collision",
    7: "max_collision",
    8: "periodicity",
    9: "covariance",
    10: "compression",
}

# test chosen for counters distribution
test = test_list[distribution_test_index]


def file_info():
    f = open(file, "r+b")
    f.seek(0, 2)
    size = f.tell()
    print("FILE INFO")
    print("Size of file is:", size, "bytes")
    print("Number of symbols per sequence for counters analysis:", n_symbols_stat)
    print("Number of sequences wanted for counters analysis:", n_sequences_stat)
    max_symbols = size * 2  # total number of symbols in the file
    max_sequences = max_symbols / n_symbols_stat
    print("Maximum sequences that can be generated from the file:", max_sequences)
    tot_seqs = n_iterations_c_stat * n_sequences_stat
    print("Total sequences necessary =", tot_seqs)
    if not bool_shuffle_stat:
        if tot_seqs <= max_sequences:
            print("SHUFFLE FROM FILE ALLOWED WITH THIS FILE")
        else:
            print("Error: SHUFFLE FROM FILE NOT ALLOWED WITH THIS FILE")
            exit(-1)
    print("----------------------------------------------------------------\n")


def config_info():
    print("CONFIG INFO - NIST")
    print("Number of symbols per sequence =", n_symbols)
    print("Number of shuffled sequences =", n_sequences)
    ts = [test_list.get(i) for i in test_list_indexes]
    print("Tests for entropy validation selected:", ts)
    if bool_first_seq:
        print("Reference sequence read from the beginning of the file")
    else:
        print("Reference sequence read from the end of the file")
    if bool_pvalue:
        print("p parameter used: NIST")
    else:
        print("p parameter used: user value \n")

    print("\nCONFIG INFO - STATISTICAL ANALYSIS")
    print("Number of symbols per sequence =", n_symbols_stat)
    print("Number of shuffled sequences =", n_sequences_stat)
    print("Number of iterations for counter:", n_iterations_c_stat)
    print("Test selected for counter distribution analysis:", test)
    comp = [test_list.get(i) for i in ref_numbers]
    print("Tests selected test for shuffle/random comparison:", comp)
    print("p parameter used: user value:", p_value_stat)
    print("----------------------------------------------------------------\n \nMAIN")
