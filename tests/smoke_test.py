import contextlib
import pathlib
import sys

import pytest

import main_parallelized
import utils.config

CONF_MINIMAL = """[global]
input_file = "minimal.bin"
test_nist = true
stat_analysis = true
[nist_test]
n_symbols = 8
n_sequences = 1
plot = true
[statistical_analysis]
n_sequences = 4
n_symbols = 256
n_iterations_c = 20
distribution_test_index = 6
ref_numbers = [6]"""


@pytest.fixture(scope="session")
def tmpdir(tmpdir_factory):
    tmpdir = pathlib.Path(tmpdir_factory.mktemp("tmpdir"))
    (tmpdir / "results").mkdir()
    (tmpdir / "conf.toml").write_text(CONF_MINIMAL, "utf-8")
    (tmpdir / "minimal.bin").write_bytes(
        bytes.fromhex(
            "b9106923e9d7b5f45a009f02ded16959573e302eddd9ad65d161fd6be9766bb4"
            + "56df6209dbf7438969c074d9f74455d16f258c7d3f9624e9cd6b6f50d6e4ed49"
            + "b8b7ad1706aa3578dc1ec31844dc2726eca2fd2687f6b692d5255a01ae53ed31"
            + "ca29e178af820456e7b5debc2f82c55b0e984b544e49891e622d09bb15a741de"
            + "29e0e77c8f318d476a47910935418b3cba8055b3a45f0c4bd7344e9b0e1a2581"
            + "5bc79d5f2875dc3e481ddd9996c9f46d9a6e681bfc164eae0e4d9093ab69a9ba"
            + "0c0b46b3d5454fd4b27f45ee62ffa23bd698f8c144b3269224de13d4ae92f391"
            + "faf5af763fb070c792b2cd6e1e588f88d7c9d701ecddf61dbc44a0e9cc880568"
            + "4f166868eec63d3a73dab5f8d8d4be137483c1a730b6c1d7ef21c1b1b13a163d"
            + "fbdb21ef50bcec09d3b39cd4802f4a02b25e2c2f543c1e598fb62a7f3a09610e"
            + "e6edd0dd2c50476c8abe95e3e073856585e924dc7a0147646d96318ba6057376"
            + "bca61e4c30d5aa35dd8fe5940c523b2ad434a4fd13d0e7c0fb0aaaa616610480"
            + "6d032a1dd56ca72ded57f50d2c624d5165335434f28f0029c64bd2bcdd0d45dd"
            + "bd4f95034bde05e186335f49051592b7b08e8fd7179720b57f79fa1644be040c"
            + "8120b1c39bcbe7f6bd0fd00423632070988d1dc3f4c1b3febef3d1ea164094e2"
            + "6504716df7cee92dfe1d5b435948bd074b3a90fe4fc15f4fdb106ce5af526813"
        )
    )
    return tmpdir


def test_main(monkeypatch, tmpdir):
    """Test that the main function executes without exceptions."""
    with monkeypatch.context() as m:
        m.setattr(sys, "argv", ["main_parallelized_test"])
        with contextlib.chdir(tmpdir):
            main_parallelized.main()


def test_iid(tmpdir):
    """Test that the IID Testing function executes without exceptions."""
    utils.config.config_data = utils.config.parse_config_file(tmpdir / "conf.toml")
    main_parallelized.iid_test_function()


def test_statistical_analysis(tmpdir):
    """Test that the statistical analysis function executes without exceptions."""
    utils.config.config_data = utils.config.parse_config_file(tmpdir / "conf.toml")
    main_parallelized.statistical_analysis_function()
