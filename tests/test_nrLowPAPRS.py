import numpy as np
import pytest

from py3gpp import nrLowPAPRS


def test_nrLowPAPRS_unit_magnitude():
    seq = nrLowPAPRS(129, 839)
    assert seq.shape == (839,)
    assert np.allclose(np.abs(seq), 1.0)


def test_nrLowPAPRS_matches_formula():
    u, N = 25, 63
    m = np.arange(N)
    expected = np.exp(-1j * np.pi * u * m * (m + 1) / N)
    assert np.allclose(nrLowPAPRS(u, N), expected)


def test_nrLowPAPRS_requires_odd_length():
    with pytest.raises(AssertionError):
        nrLowPAPRS(1, 64)


def test_nrLowPAPRS_requires_coprime():
    with pytest.raises(AssertionError):
        nrLowPAPRS(3, 9)  # gcd(3, 9) == 3, not coprime
