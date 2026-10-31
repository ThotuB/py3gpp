import matlab.engine
import numpy as np
import pytest

from py3gpp import nrPUCCHHoppingInfo


def run_nr_pucch_hopping_info(cp, nslot, nid, grouphopping, initialcs, seqcs, eng):
    info = nrPUCCHHoppingInfo(cp, nslot, nid, grouphopping, initialcs, seqcs)

    ref = eng.nrPUCCHHoppingInfo(cp, nslot, nid, grouphopping, initialcs, seqcs)
    u_ref = np.asarray(ref["U"]).ravel().astype(int)
    v_ref = np.asarray(ref["V"]).ravel().astype(int)
    alpha_ref = np.asarray(ref["Alpha"]).ravel()

    assert np.array_equal(info["U"], u_ref)
    assert np.array_equal(info["V"], v_ref)
    assert np.allclose(info["Alpha"], alpha_ref, atol=1e-6)


@pytest.mark.parametrize("grouphopping", ["neither", "enable", "disable"])
@pytest.mark.parametrize("cp", ["normal", "extended"])
def test_nr_pucch_hopping_info_matlab(cp, grouphopping, eng):
    run_nr_pucch_hopping_info(cp, 3, 512, grouphopping, 5, 2, eng)


@pytest.mark.parametrize("nid", [0, 29, 30, 512, 1023])
def test_nr_pucch_hopping_info_nid_sweep_matlab(nid, eng):
    run_nr_pucch_hopping_info("normal", 7, nid, "enable", 5, 0, eng)


def test_nr_pucch_hopping_info_sequence_hopping_matlab(eng):
    run_nr_pucch_hopping_info("extended", 7, 12, "disable", 9, 4, eng)
