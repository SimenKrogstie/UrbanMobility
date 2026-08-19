def test_mobility_public_api():
    from urbanmobility import mobility

    assert callable(mobility.calculate_mobility_indicators)
    assert callable(mobility.plot_mobility_indicators)
    assert callable(mobility.plot_timeprofile)
    assert callable(mobility.plot_timeprofile_directions)


def test_mobility_exports():
    from urbanmobility import mobility

    assert set(mobility.__all__) == {
        "calculate_mobility_indicators",
        "plot_mobility_indicators",
        "plot_timeprofile",
        "plot_timeprofile_directions",
    }
