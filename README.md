# Entropy validation

![Black|main](https://github.com/RandomPower/IID_validation/actions/workflows/black.yml/badge.svg?branch=main)
![flake8|main](https://github.com/RandomPower/IID_validation/actions/workflows/flake8.yml/badge.svg?branch=main)
![isort|main](https://github.com/RandomPower/IID_validation/actions/workflows/isort.yml/badge.svg?branch=main)

This project aims to provide a third entropy validation test suite, beyond the NIST randomness test suite [SP 800-22r1a](https://csrc.nist.gov/projects/random-bit-generation/documentation-and-software) and the [TestU01](https://simul.iro.umontreal.ca/testu01/tu01.html) suite.

This test suite, called IID_Validation (temporary name) implements three statistical measures to be computed over random bit sequences:

1. Testing of the IID Assumption (NIST [SP 800-90B](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-90B.pdf))
2. A RandomPower-specific statistical analysis suite (TODO: fill in)
3. Calculation of the [Min-Entropy](https://en.wikipedia.org/wiki/Min-entropy)

## The IID_validation test suite

The suite is implemented in Python 3 as the `main_parallelized.y` Python program:

```
$ main_parallelized.py --help
```

TODO: fill this section

## Installing the software

The software is distributed with a list of requirements contained in `requirements.txt`. It is recommended to install the dependencies and run the software inside a Python virtual environment.

For example, using `venv`:

```shell
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
(.venv) $ python main_parallelized.py --help
```

The main dependencies of the IID_Validation test suite are `numpy`, `matplotlib` and the `tqdm` utility library.

## NIST IID test suite indexes

Our implementation of the NIST IID test suite uses the following indexes to refer to the permutation tests:

| Index | NIST SP 800-90B reference                      |
|:-----:|:-----------------------------------------------|
|  0    | **5.1.1** - Excursion Test Statistic           |
|  1    | **5.1.2** - Number of Directional Runs         |
|  2    | **5.1.3** - Length of Directional Runs         |
|  3    | **5.1.4** - Number of Increases and Decreases  |
|  4    | **5.1.5** - Number of Runs Based on the Median |
|  5    | **5.1.6** - Length of Runs Based on Median     |
|  6    | **5.1.7** - Average Collision Test Statistic   |
|  7    | **5.1.8** - Maximum Collision Test Statistic   |
|  8    | **5.1.9** - Periodicity Test Statistic         |
|  9    | **5.1.10** - Covariance Test Statistic         |
| 10    | **5.1.11** - Compression Test Statistic        |

For more information on the individual tests, refer to [NIST SP 800-90B](https://csrc.nist.gov/pubs/sp/800/90/b/final).

## Program configuration
Program options can be set in a TOML configuration file, or on the command line.
The software contains default values for all parameters except the input file: values specified in the configuration file have precedence over the defaults, and values specified on the command line have precedence over any others.

A concise description of the options is available by running the program with the `--help` option, while a full description can be found in the following subsections.

Program options are divided into three groups: global, NIST test and Statistical analysis.

### Global
These options configure the overall operation of the software. They can be specified in the configuration file (see `-c, --config` option) in the `[global]` section.

- `-c CONFIG`, `--config CONFIG` \
    The configuration file, in TOML format.

    It can be specified as an absolute or relative path. If relative, it will be interpreted as relative to the current directory.
    If not specified, the program will look for a `conf.toml` in the current directory.

    A configuration file can contain no, some, or all possible parameters.
    You can find a [reference configuration file](conf.toml) in the repo.

    **Note**: this option cannot be specified in the config file.

- `-i INPUT_FILE`, `--input_file INPUT_FILE` \
    The binary input file containing the random bits to analyze.

    It can be specified as an absolute or relative path. If relative, it will be interpreted as relative to the current directory.
    The accepted file extensions are `.bin` and `.dat` (case-insensitive).

- `-t`, `--nist_test`, `--no-nist_test` \
    Enables the NIST IID validation process on the input file.

    Active by default.

- `-a`, `--stat_analysis`, `--no-stat_analysis` \
    Enables the Random Power statistical analysis on the input file.

    Enabled by default.

- `-e`, `--min_entropy`, `--no-min_entropy` \
    Enables the min-entropy calculation on the input file.

    Enabled by default.

- `--parallel`, `--no-parallel` \
    Run the NIST permutation tests in parallel, using multiprocessing.

    The number of parallel processes corresponds to the number of CPUs available on the system.

    Enabled by default.

- `-d`, `--debug` \
    Show debug messages on the command line.

    Debug messages are always saved in the application log file saved in each result folder.

    False by default.

### NIST test

These options configure the NIST permutation tests. They can be specified in the configuration file (see `-c, --config` option) in the `[nist_test]` section.

- `--nist_selected_tests INDEX [INDEX ...]` \
    The permutation tests to execute for the IID validation process. Supported values are described in [NIST IID test suite indexes](#nist-iid-test-suite-indexes).

    All tests are enabled by default.

- `--nist_n_symbols NIST_N_SYMBOLS` \
    The number of symbols to analyze.

    The NIST tests require a minimum number of symbols greater than the alphabet size (number of possible symbol values).
    Since our application only supports 4-bit symbols (for now), the corresponding alphabet size is 2^4 = 16.

    This number cannot be more than the number of symbols contained in the input file. Since our application only supports 4-bit symbols (for now), the number of symbols in the input file is double the number of bytes in the file.

    Set to 1000000 (10^6) by default.

- `--nist_n_permutations NIST_N_PERMUTATIONS` \
    The number of Fisher-Yates permutations to generate from the input sequence.

    Set to 10000 (10^4) by default.

- `--first_seq` \
    Test the first symbol sequence from the input file. Mutually exclusive with `--last_seq`.

    Enabled by default.

- `--last_seq` \
    Test the last symbol sequence from the input file. Mutually exclusive with `--first_seq`.

    Disabled by default.

- `--plot`, `--no-plot` \
    Enables the generation of a histogram plot for each of the executed tests.

    Enabled by default.

- `--nist_p P [P ...]` \
    The lag parameters p used for the periodicity and covariance tests.

    Each p value has to be included in the open interval (0, nist_n_symbols).

    Set to the NIST SP-800-90B values [1, 2, 8, 16, 32] by default.

### Statistical Analysis

These options configure the Random Power statistical analysis part, described in section [TBD](#tbd).

- `--stat_selected_tests INDEX [INDEX ...]` \
    The permutation tests to execute for the Random Power statistical analysis. Supported values are described in [NIST IID test suite indexes](#nist-iid-test-suite-indexes).

    All tests are enabled by default.

- `--stat_n_symbols STAT_N_SYMBOLS` \
    The number of symbols to analyze.

    The NIST tests require a minimum number of symbols greater than the alphabet size (number of possible symbol values).
    Since our application only supports 4-bit symbols (for now), the corresponding alphabet size is 2^4 = 16.

    This number cannot be more than the number of symbols contained in the input file. Since our application only supports 4-bit symbols (for now), the number of symbols in the input file is double the number of bytes in the file.

    Set to 1000 (10^3) by default.

- `--stat_n_permutations STAT_N_PERMUTATIONS`  \
    The number of Fisher-Yates permutations to generate from the input sequence.

    Set to 200 by default.

- `--stat_n_iterations STAT_N_ITERATIONS` \
    The number of iterations of the IID test suite to obtain the statistical distribution of counter C0.

    Set to 500 by default.

- `--stat_p P` \
    The lag parameter p used for the periodicity and covariance tests.

    Only one value of p is used in the Random Power statistical analysis, in contrast with the generic NIST test suite.
    The value has to be included in the open interval (0, nist_n_symbols).

    Set to 2 by default.
