import matlab.engine
import numpy as np
import pytest

from py3gpp import nrPUCCH1


def _col(x):
    return matlab.double([[v] for v in x])


def run_nr_pucch1(ack, sr, symallocation, cp, nslot, nid, grouphopping, initialcs, freqhopping, occi, eng):
    sym = nrPUCCH1(ack, sr, symallocation, cp, nslot, nid, grouphopping, initialcs, freqhopping, occi)

    ref = eng.nrPUCCH1(
        _col(ack),
        _col(sr),
        matlab.double(symallocation),
        cp,
        nslot,
        nid,
        grouphopping,
        initialcs,
        freqhopping,
        occi,
    )
    ref = np.array(ref).ravel()

    assert sym.shape == ref.shape
    assert np.allclose(sym, ref, atol=1e-6)


def test_nr_pucch1_1bit_no_hopping_matlab(eng):
    run_nr_pucch1([1], [0], [0, 14], "normal", 3, 512, "enable", 5, "disabled", 0, eng)


def test_nr_pucch1_2bit_intraslot_hopping_matlab(eng):
    run_nr_pucch1([1, 0], [], [0, 10], "normal", 7, 100, "enable", 3, "enabled", 1, eng)


@pytest.mark.parametrize("occi", [0, 1, 2])
def test_nr_pucch1_occi_sweep_matlab(occi, eng):
    run_nr_pucch1([0], [1], [0, 12], "extended", 5, 300, "disable", 4, "disabled", occi, eng)


def test_nr_pucch1_short_allocation_matlab(eng):
    run_nr_pucch1([1], [0], [10, 4], "normal", 0, 42, "neither", 0, "disabled", 0, eng)
