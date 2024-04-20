import pathlib

import pytest

import main_parallelized
import utils

CONF_MINIMAL = """[global]
input_file = "{}"
bool_test_NIST = true
bool_statistical_analysis = true
test_list_indexes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
[nist_test]
n_symbols = 8
n_sequences = 1
bool_shuffle_NIST = true
bool_first_seq = true
bool_pvalue = false
p = [1, 2, 8, 16, 32]
see_plots = true
[statistical_analysis]
n_sequences_stat = 1
n_symbols_stat = 8
n_iterations_c_stat = 1
distribution_test_index = 6
bool_shuffle_stat = true
p_value_stat = 2
ref_numbers = [1, 3, 4]"""


@pytest.fixture(scope='session')
def tmpdir(tmpdir_factory):
    tmpdir = pathlib.Path(tmpdir_factory.mktemp('tmpdir'))
    (tmpdir / "conf.toml").write_text(CONF_MINIMAL.format(pathlib.PurePosixPath(tmpdir / "MINIMAL.BIN")), "utf-8")
    (tmpdir / "MINIMAL.BIN").write_bytes(bytes.fromhex("b9106923e9d7b5f45a009f02ded16959"))
    return tmpdir


def test_main(tmpdir):
    """Test that the main function executes without exceptions."""
    utils.config.config_data = utils.config.parse_config_file(tmpdir / "conf.toml")
    main_parallelized.main()


def test_iid(tmpdir):
    """Test that the IID Testing function executes without exceptions."""
    utils.config.config_data = utils.config.parse_config_file(tmpdir / "conf.toml")
    main_parallelized.iid_test_function()


def test_statistical_analysis(tmpdir):
    """Test that the statistical analysis function executes without exceptions."""
    utils.config.config_data = utils.config.parse_config_file(tmpdir / "conf.toml")
    main_parallelized.statistical_analysis_function()
