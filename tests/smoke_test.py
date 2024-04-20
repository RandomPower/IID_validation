import main_parallelized


def test_main():
    """Test that the main function executes without exceptions."""
    main_parallelized.main()


def test_iid():
    """Test that the IID Testing function executes without exceptions."""
    main_parallelized.iid_test_function()


def test_statistical_analysis():
    """Test that the statistical analysis function executes without exceptions."""
    main_parallelized.statistical_analysis_function()