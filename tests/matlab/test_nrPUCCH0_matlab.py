import matlab.engine
import numpy as np
import pytest

from py3gpp import nrPUCCH0


def _col(x):
    return matlab.double([[v] for v in x])


def run_nr_pucch0(ack, sr, symallocation, cp, nslot, nid, grouphopping, initialcs, freqhopping, eng):
    sym = nrPUCCH0(ack, sr, symallocation, cp, nslot, nid, grouphopping, initialcs, freqhopping)

    ref = eng.nrPUCCH0(
        _col(ack),
        _col(sr),
        matlab.double(symallocation),
        cp,
        nslot,
        nid,
        grouphopping,
        initialcs,
        freqhopping,
    )
    ref = np.array(ref).ravel()

    assert sym.shape == ref.shape
    assert np.allclose(sym, ref, atol=1e-6)


def test_nr_pucch0_sr_only_matlab(eng):
    run_nr_pucch0([], [1], [11, 2], "normal", 63, 512, "enable", 5, "disabled", eng)


def test_nr_pucch0_2bit_ack_matlab(eng):
    run_nr_pucch0([1, 1], [0], [10, 2], "extended", 3, 12, "enable", 5, "disabled", eng)


def test_nr_pucch0_freq_hopping_2symbol_matlab(eng):
    run_nr_pucch0([1, 0], [], [0, 2], "normal", 5, 100, "disable", 3, "enabled", eng)


@pytest.mark.parametrize("nslot", [0, 1, 7, 19])
@pytest.mark.parametrize("ack", [[0], [1]])
def test_nr_pucch0_1bit_ack_sweep_matlab(ack, nslot, eng):
    run_nr_pucch0(ack, [0], [12, 2], "normal", nslot, 200, "enable", 7, "disabled", eng)


def test_nr_pucch0_sequence_hopping_matlab(eng):
    run_nr_pucch0([0, 1], [], [0, 2], "normal", 9, 300, "disable", 4, "disabled", eng)
