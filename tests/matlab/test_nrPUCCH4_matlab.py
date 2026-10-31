import matlab.engine
import numpy as np
import pytest

from py3gpp import nrPUCCH4


def run_nr_pucch4(uciCW, modulation, nid, rnti, sf, occi, eng):
    sym = nrPUCCH4(uciCW, modulation, nid, rnti, sf, occi)

    ref = eng.nrPUCCH4(matlab.double([[v] for v in uciCW.tolist()]), modulation, nid, rnti, sf, occi)
    ref = np.array(ref).ravel()

    assert sym.shape == ref.shape
    assert np.allclose(sym, ref, atol=1e-6)


@pytest.mark.parametrize("modulation", ["QPSK", "pi/2-BPSK"])
@pytest.mark.parametrize("sf,occi", [(2, 0), (2, 1), (4, 0), (4, 3)])
def test_nr_pucch4_sf_occi_sweep_matlab(modulation, sf, occi, eng):
    bps = 2 if modulation == "QPSK" else 1
    nbits = 12 * bps * 8
    rng = np.random.default_rng(sf * 100 + occi * 10 + hash(modulation) % 7)
    uciCW = rng.integers(0, 2, nbits)
    run_nr_pucch4(uciCW, modulation, 55, 321, sf, occi, eng)
