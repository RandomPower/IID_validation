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

The following is the list of test indexes used in the software, specifically for the **NIST IID test suite**. On the left, there are the indexes used in the program, while, on the right, the associated references.

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

For more, refer to the **NIST SP 800-90B Recommendation**.

## A guide to the command line options
The command line represent a quick and convenient tool to set parameters, without the need to change parameter values in the configuration file each time. \
The options are visible (with their description) by specifying the flag `--help`, when executing the program.

They are divided into three groups:

1. Global - these options configure the overall operation of the sofware and include:
    - `-c CONFIG` or `--config CONFIG` \
        The **TOML configuration file** to read.

        A configuration file can be empty, contain some of the parameters, or all of them. The only mandatory parameter is the input file, as the software works on it, while the other parameters have default values embedded in the software. 
        
        The path for the configuration file can be specified either as absolute or as the file name only. In the latter case, it will be interpreted as relative to the executable program directory.

        Below an example of configuration file, in which all configurable parameters are specified:
        ```toml
        [global]
        input_file = "getbits_20230401_195315_RAW_BITS.BIN"
        nist_test = true
        stat_analysis = false

        [nist_test]
        selected_tests = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        n_symbols = 1000
        n_permutations = 100000
        first_seq = true
        plot = false
        p = [2]

        [statistical_analysis]
        selected_tests = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        n_permutations = 20
        n_symbols = 100
        n_iterations = 50
        p = 2
        ``` 
        Any custom configuration file has to follow the structure above, otherwise it will **NOT** work.
    
    - `-i INPUT_FILE` or `--input_file INPUT_FILE` \
        The path to the raw-bit input file that the software has to analyze. Like for the configuration file, the path can be either absolute or comprise the file name only, in which case it will be interpreted relative to the executable directory. The accepted file extensions are **.bin**, **.BIN**, **.dat**, and **.DAT**.

    - `-t` or `--nist_test` \
        Enables the IID validation process on the input file. By default, it's active, but it can be de-activated by specifying `--no-nist_test`.

    - `-a` or `--stat_analysis` \
        Enables the Random Power statistical analysis on the input file. Like the previous option, it's active by default and can be deactivated by specifying `--no-stat_analysis`.

    - `--parallel` \
    Enables the program execution in parallel mode, utilizing multiple CPUs. By default, it's active and can be de-activated by specifying `--no-parallel`. The number of parallel processes corresponds to the number of
    available processors at a given moment. In particular, only the NIST permutation test is affected by this option.

The meaning of the remaining parameters will be illustrated in their respective sub-sections below.

2. Nist Test - these options need to be configured to carry out the IID validation process and comprise:
    - `--nist_selected_tests INDEX [INDEX ...]` \
        Sets the statistical tests to perform in the IID validation process. Refer to the section above (**NIST IID test suite indexes**) for more details. Any test number not comprised in the table above will be considered invalid. Some examples on how to specify the test:
        - The specified tests can either be multiple:
            ```bash
            python3 main_parallelized.py --nist_selected_test 1 2 3
            ```
        - or just a single one:
            ```bashconcurrent
            python3 main_parallelized.py --nist_selected_test 10
            ```
        By default, all tests are enabled.

    - `--nist_n_symbols NIST_N_SYMBOLS` \
        Specifies the number of symbols contained in the sequence to analyze. It's value must be greater than or equal to 16, as each of the symbols produced has a length of 4. By default, it's set to 1'000'000.

    - `--nist_n_permutations NIST_N_PERMUTATIONS` \
        Specifies the number of permutations to generate, starting from the sequence of `nist_n_symbols` symbols. By default, it's set to 10'000.

    - `--first_seq` \
        Enables testing on the first sequence of [nist_n_symbols] symbols from the input file. This option and `--last_seq` are mutually exclusive.
        To enable it:
            ```bash
            python3 main_parallelized.py --first_seq
            ```
        By default, this option is enabled.

    - `--last_seq` \
        Enables testing on the last sequence of [nist_n_symbols] symbols from the input file. It must be specified as `--first_seq`. By default, it's disabled.

    - `--plot` or `--no-plot` \
        Enables the generation of a histogram plot for each of the executed tests and saves them to a pre-defined folder. By default, it's active. 

    - `--nist_p P [P ...]` \
        Set the lag parameters p used for the periodicity and the covariance tests. Each p value has to be included in the interval (0, nist_n_symbols), extremes excluded. The default value set is [1, 2, 8, 16, 32].

3. Statistical Analysis - these options are related to the **Random Power** statistical analysis part, which is an additional custom tool we implemented. It specifies as parameters:
    - `--stat_selected_tests INDEX [INDEX ...]` \
        Sets the tests to execute, when performing the Random Power statistical analysis. Refer to the section above (**NIST IID test suite indexes**) for more details. Just as for the NIST counterpart, it can be specified in two ways:
        - The specified tests can either be multiple:
            ```bash
            python3 main_parallelized.py --stat_selected_test 1 2 3
            ```
        - or just a single one:
            ```bashconcurrent
            python3 main_parallelized.py --stat_selected_test 10
            ```
        By default, all tests are enabled.

    - `--stat_n_permutations STAT_N_PERMUTATIONS`  \
        Sets the number of permutations to test. The default value is 200.

    - `--stat_n_symbols STAT_N_SYMBOLS` \
        Sets the number of symbols in a sequence. It's value must be greater or equal to 16, as each of the symbols produced has a length of 4. The default value is 1'000.

    - `--stat_n_iterations STAT_N_ITERATIONS` \
        Sets the number of iterations of the IID test suite to obtain the statistical distribution of counter C0. The default values is 500.

    - `--stat_p P` \
        Sets the lag parameter P used for the periodicity and the covariance tests. This value has to be included in the interval (0, stat_n_symbols), extremes excluded. The default value is 2.
