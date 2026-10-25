import numpy as np

from py3gpp import nrPUCCHHoppingInfo


def test_nrPUCCHHoppingInfo_docstring_example1():
    # Reference values from nrPUCCHHoppingInfo.m's own documented Example 1.
    info = nrPUCCHHoppingInfo("normal", 3, 512, "enable", 5, 0)

    assert info["U"].tolist() == [13, 22]
    assert info["V"].tolist() == [0, 0]
    expectedAlpha = [
        2.0944,
        2.0944,
        0,
        5.7596,
        2.6180,
        3.6652,
        4.1888,
        5.7596,
        1.5708,
        5.2360,
        5.2360,
        3.1416,
        0.5236,
        5.2360,
    ]
    assert np.allclose(info["Alpha"], expectedAlpha, atol=1e-4)
    assert info["FGH"].tolist() == [11, 20]
    assert info["FSS"] == 2
    assert info["Hopping"] == "groupHopping"
    expectedNcs = [239, 107, 223, 6, 24, 2, 3, 66, 238, 125, 209, 145, 44, 233]
    assert info["NCS"].tolist() == expectedNcs


def test_nrPUCCHHoppingInfo_docstring_example2():
    # Reference values from nrPUCCHHoppingInfo.m's own documented Example 2, confirmed via a
    # live MATLAB 5G Toolbox (R2026a) session (the docstring itself doesn't print the numbers).
    info = nrPUCCHHoppingInfo("extended", 7, 12, "enable", 9, 0)

    u = info["U"][0]
    v = info["V"][0]
    alpha = info["Alpha"][4]

    assert u == 20
    assert v == 0
    assert np.isclose(alpha, 5.7595865316, atol=1e-6)
    assert info["FGH"].tolist() == [8, 22]
    assert info["FSS"] == 12
    assert info["Hopping"] == "groupHopping"
