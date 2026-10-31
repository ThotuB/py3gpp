import numpy as np
import pytest

from py3gpp import nrSSBurstStartSymbols


def run_nr_ssburst_start_symbols(case_name, lmax, eng):
    starts = nrSSBurstStartSymbols(case_name, lmax)

    burst = {"BlockPattern": f"Case {case_name}", "TransmittedBlocks": [1.0] * lmax}
    ref = eng.feval("nr5g.internal.wavegen.hSSBurstStartSymbols", burst)
    ref = np.asarray(ref).ravel().astype(int)

    assert starts.shape == ref.shape
    assert np.array_equal(starts, ref)


@pytest.mark.parametrize("lmax", [4, 8])
@pytest.mark.parametrize("case_name", ["A", "B", "C"])
def test_nr_ssburst_start_symbols_fr1_matlab(case_name, lmax, eng):
    run_nr_ssburst_start_symbols(case_name, lmax, eng)


@pytest.mark.parametrize("case_name", ["D", "E", "F", "G"])
def test_nr_ssburst_start_symbols_fr2_matlab(case_name, eng):
    run_nr_ssburst_start_symbols(case_name, 64, eng)
