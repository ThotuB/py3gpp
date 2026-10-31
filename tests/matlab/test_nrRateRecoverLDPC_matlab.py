import matlab.engine
import numpy as np
import pytest

from py3gpp.plc.trs.ldpc import nrRateRecoverLDPC


@pytest.mark.parametrize("N", [4500])
@pytest.mark.parametrize("trblklen", [4000])
@pytest.mark.parametrize("R", [0.5, 0.9])
@pytest.mark.parametrize("rv", [0, 1, 2, 3])
@pytest.mark.parametrize("mod", ["QPSK"])
@pytest.mark.parametrize("nLayers", [1])
@pytest.mark.parametrize("numCB", [1])
def test_nrRateRecoverLDPC_matlab(N, trblklen, R, rv, mod, nLayers, numCB, eng):
    # soft bits before code block desegmentation
    llr_max = 65000
    sbits = np.random.random_sample((N, 1)) * 2 * llr_max - llr_max
    ref_data = eng.nrRateRecoverLDPC(
        eng.double(sbits),
        eng.double(trblklen),
        eng.double(R),
        eng.double(rv),
        mod,
        eng.double(nLayers),
        eng.double(numCB),
    )
    ref_data = np.asarray(ref_data)
    out_data = nrRateRecoverLDPC(sbits, trblklen, R, rv, mod, nLayers, numCB)
    assert np.array_equal(ref_data, out_data)
