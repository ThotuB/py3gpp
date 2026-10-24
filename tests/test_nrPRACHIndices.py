import sys

import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrPRACHConfig, nrPRACHIndices

sys.path.append("test_data")

from test_data.prach import prach_cfg0_ind_ref


def test_nrPRACHIndices_matches_matlab_reference():
    carrier = nrCarrierConfig()
    prach = nrPRACHConfig()
    prach.ConfigurationIndex = 0
    prach.NPRACHSlot = 11

    ind = nrPRACHIndices(carrier, prach)
    assert np.array_equal(ind, prach_cfg0_ind_ref)


def test_nrPRACHIndices_inactive_slot_returns_empty():
    carrier = nrCarrierConfig()
    prach = nrPRACHConfig()
    prach.ConfigurationIndex = 0
    prach.NPRACHSlot = 0

    ind = nrPRACHIndices(carrier, prach)
    assert ind.shape == (0,)


def test_nrPRACHIndices_formats_1_and_2():
    # Spot-checked against a live MATLAB session (see plan/context): both formats produce a
    # contiguous run of PRACHDuration * 839 indices in the PRACH-grid's own (finer) numerology.
    carrier = nrCarrierConfig()
    for configurationIndex, nprachslot, expectedLen, expectedFirst, expectedLast in [
        (28, 3, 839 * 2, 7, 8333),
        (53, 2, 839 * 4, 7, 23309),
    ]:
        prach = nrPRACHConfig()
        prach.ConfigurationIndex = configurationIndex
        prach.NPRACHSlot = nprachslot

        ind = nrPRACHIndices(carrier, prach)
        assert ind.shape == (expectedLen,)
        assert ind[0] == expectedFirst
        assert ind[-1] == expectedLast
        assert len(np.unique(ind)) == ind.size


def test_nrPRACHIndices_format3_not_implemented():
    carrier = nrCarrierConfig()
    prach = nrPRACHConfig()
    prach.ConfigurationIndex = 60  # Format 3
    with pytest.raises(NotImplementedError):
        nrPRACHIndices(carrier, prach)
