import numpy as np
import pytest

from py3gpp import nrSSBurstStartSymbols


def test_case_a_lmax4():
    starts = nrSSBurstStartSymbols("A", 4)
    assert np.array_equal(starts, [2, 8, 16, 22])


def test_case_a_lmax8():
    starts = nrSSBurstStartSymbols("A", 8)
    assert np.array_equal(starts, [2, 8, 16, 22, 30, 36, 44, 50])


def test_case_b_lmax8():
    starts = nrSSBurstStartSymbols("B", 8)
    assert np.array_equal(starts, [4, 8, 16, 20, 32, 36, 44, 48])


def test_case_name_accepts_case_prefix():
    starts_short = nrSSBurstStartSymbols("A", 8)
    starts_long = nrSSBurstStartSymbols("Case A", 8)
    assert np.array_equal(starts_short, starts_long)


@pytest.mark.parametrize("case_name", ["D", "E", "F", "G"])
def test_fr2_cases_lmax64(case_name):
    starts = nrSSBurstStartSymbols(case_name, 64)
    assert starts.shape == (64,)
    assert len(np.unique(starts)) == 64


@pytest.mark.parametrize("case_name", ["A", "B", "C"])
def test_fr1_cases_invalid_lmax_raises(case_name):
    with pytest.raises(AssertionError):
        nrSSBurstStartSymbols(case_name, 64)


@pytest.mark.parametrize("case_name", ["D", "E", "F", "G"])
def test_fr2_cases_invalid_lmax_raises(case_name):
    with pytest.raises(AssertionError):
        nrSSBurstStartSymbols(case_name, 8)


def test_invalid_case_name_raises():
    with pytest.raises(AssertionError):
        nrSSBurstStartSymbols("H", 8)
