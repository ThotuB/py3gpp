import numpy as np
import pytest

from py3gpp import nrPDCCH, nrPDCCHDecode


@pytest.mark.parametrize("rnti", [1, 1234, 65535])
@pytest.mark.parametrize("nid", [0, 42, 1007])
def test_nrPDCCH_nrPDCCHDecode(rnti, nid):
    bits = np.random.randint(0, 2, size=200)
    sym = nrPDCCH(bits, rnti, nid)
    assert sym.shape == (100,)

    soft = nrPDCCHDecode(sym, rnti, nid)
    recovered = (soft < 0).astype(int)
    assert np.array_equal(recovered, bits)
