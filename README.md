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
