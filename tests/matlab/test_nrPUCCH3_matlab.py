import matlab.engine
import numpy as np
import pytest

from py3gpp import nrPUCCH3


def run_nr_pucch3(uciCW, modulation, nid, rnti, mrb, eng):
    sym = nrPUCCH3(uciCW, modulation, nid, rnti, mrb)

    ref = eng.nrPUCCH3(matlab.double([[v] for v in uciCW.tolist()]), modulation, nid, rnti, mrb)
    ref = np.array(ref).ravel()

    assert sym.shape == ref.shape
    assert np.allclose(sym, ref, atol=1e-6)


@pytest.mark.parametrize("modulation", ["QPSK", "pi/2-BPSK"])
@pytest.mark.parametrize("mrb", [1, 4, 12])
def test_nr_pucch3_modulation_mrb_sweep_matlab(modulation, mrb, eng):
    nbits = mrb * 12 * (2 if modulation == "QPSK" else 1) * 10
    rng = np.random.default_rng(mrb * 10 + hash(modulation) % 7)
    uciCW = rng.integers(0, 2, nbits)
    run_nr_pucch3(uciCW, modulation, 77, 123, mrb, eng)
