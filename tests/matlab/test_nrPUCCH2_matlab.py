import matlab.engine
import numpy as np
import pytest

from py3gpp import nrPUCCH2


def run_nr_pucch2(uciCW, nid, rnti, eng):
    sym = nrPUCCH2(uciCW, nid, rnti)

    ref = eng.nrPUCCH2(matlab.double([[v] for v in uciCW.tolist()]), nid, rnti)
    ref = np.array(ref).ravel()

    assert sym.shape == ref.shape
    assert np.allclose(sym, ref, atol=1e-6)


@pytest.mark.parametrize("nbits", [16, 48, 96])
def test_nr_pucch2_bit_length_sweep_matlab(nbits, eng):
    rng = np.random.default_rng(nbits)
    uciCW = rng.integers(0, 2, nbits)
    run_nr_pucch2(uciCW, 200, 50, eng)


def test_nr_pucch2_nid_rnti_matlab(eng):
    rng = np.random.default_rng(1)
    uciCW = rng.integers(0, 2, 32)
    run_nr_pucch2(uciCW, 1023, 65535, eng)
