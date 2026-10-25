import numpy as np
import pytest

from py3gpp import nrUCIDecode, nrUCIEncode


def _round_trip(A, euci, modulation="QPSK", seed=0):
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, A)

    coded = nrUCIEncode(bits, euci, modulation)
    assert coded.shape == (euci,)

    # Resolve the "x"/"y" placeholder bits (-1/-2), as documented for nrUCIEncode's A<3 output.
    coded = coded.astype(float).copy()
    coded[coded == -1] = 1
    yIdx = np.where(coded == -2)[0]
    coded[yIdx] = coded[yIdx - 1]

    llr = 1 - 2.0 * coded  # perfect channel
    decoded, err = nrUCIDecode(llr, A, modulation)
    return bits, decoded, err


@pytest.mark.parametrize(
    "A,euci,modulation",
    [
        (1, 10, "QPSK"),
        (1, 12, "16QAM"),
        (2, 9, "QPSK"),
        (2, 12, "64QAM"),
        (5, 30, "QPSK"),
        (11, 50, "QPSK"),
        (30, 600, "QPSK"),  # Polar, 11-bit CRC, nmax=9
        (54, 1024, "QPSK"),  # Polar, 11-bit CRC, nmax=10
        (100, 1100, "QPSK"),
        (300, 1050, "QPSK"),
    ],
)
def test_nrUCIEncode_nrUCIDecode_round_trip(A, euci, modulation):
    bits, decoded, err = _round_trip(A, euci, modulation)
    assert np.array_equal(decoded, bits)
    assert err is False


def test_nrUCIEncode_six_bit_crc_range_not_implemented():
    # TS 38.212's N-selection formula always resolves to nmax=8 for A=12..19 (6-bit CRC),
    # but this repo's nrPolarDecode only supports nmax in {9, 10} -- a pre-existing limitation.
    rng = np.random.default_rng(0)
    bits = rng.integers(0, 2, 15)
    with pytest.raises(NotImplementedError):
        nrUCIEncode(bits, 300)


def test_nrUCIEncode_two_codeword_segmentation_not_implemented():
    rng = np.random.default_rng(0)
    bits = rng.integers(0, 2, 400)
    with pytest.raises(NotImplementedError):
        nrUCIEncode(bits, 1200)


def test_nrUCIDecode_two_codeword_segmentation_not_implemented():
    llrs = np.ones(1200)
    with pytest.raises(NotImplementedError):
        nrUCIDecode(llrs, 400)
