import numpy as np
import pytest

from py3gpp import nrDCIDecode, nrDCIEncode


@pytest.mark.parametrize("dcilen", [12, 40, 60])
@pytest.mark.parametrize("E", [512, 600, 864])
@pytest.mark.parametrize("rnti", [1, 6143, 65535])
def test_nrDCIEncode_nrDCIDecode(dcilen, E, rnti):
    dcibits = np.random.randint(0, 2, size=dcilen)
    coded = nrDCIEncode(dcibits, rnti, E)
    assert coded.shape == (E,)

    softbits = (1 - 2 * coded).astype(np.float64)
    decoded_bits, crc_result = nrDCIDecode(softbits, dcilen, rnti)
    assert crc_result == 0
    assert np.array_equal(decoded_bits, dcibits)


def test_nrDCIDecode_wrong_rnti_fails_crc():
    dcilen = 40
    E = 600
    rnti = 6143
    dcibits = np.random.randint(0, 2, size=dcilen)
    coded = nrDCIEncode(dcibits, rnti, E)
    softbits = (1 - 2 * coded).astype(np.float64)

    _, crc_result = nrDCIDecode(softbits, dcilen, rnti + 1)
    assert crc_result != 0
