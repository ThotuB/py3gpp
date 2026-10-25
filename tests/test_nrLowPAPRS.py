import numpy as np
import pytest

from py3gpp import nrLowPAPRS


@pytest.mark.parametrize("m", [6, 12, 18, 24])
def test_nrLowPAPRS_phase_table_lengths_unit_magnitude(m):
    seq = nrLowPAPRS(u=9, v=0, alpha=0, m=m)
    assert seq.shape == (m,)
    assert np.allclose(np.abs(seq), 1.0)


def test_nrLowPAPRS_m30_formula():
    u = 5
    n = np.arange(30)
    expected = np.exp(-1j * np.pi * (u + 1) * (n + 1) * (n + 2) / 31)
    assert np.allclose(nrLowPAPRS(u, 0, 0, 30), expected)


def test_nrLowPAPRS_m_above_30_unit_magnitude():
    seq = nrLowPAPRS(u=9, v=0, alpha=0, m=36)
    assert seq.shape == (36,)
    assert np.allclose(np.abs(seq), 1.0)


def test_nrLowPAPRS_vector_alpha_shape():
    seq = nrLowPAPRS(u=25, v=0, alpha=[np.pi / 2, np.pi], m=12)
    assert seq.shape == (12, 2)


def test_nrLowPAPRS_v_must_be_zero_below_72():
    with pytest.raises(AssertionError):
        nrLowPAPRS(u=20, v=1, alpha=0, m=48)


def test_nrLowPAPRS_length_must_be_multiple_of_6_below_36():
    with pytest.raises(AssertionError):
        nrLowPAPRS(u=0, v=0, alpha=0, m=20)
