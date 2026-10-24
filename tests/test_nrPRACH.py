import sys

import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrPRACH, nrPRACHConfig

sys.path.append("test_data")

from test_data.prach import prach_cfg0_seq_ref


def _active_config():
    carrier = nrCarrierConfig()
    prach = nrPRACHConfig()
    prach.FrequencyRange = "FR1"
    prach.DuplexMode = "FDD"
    prach.ConfigurationIndex = 0
    prach.SequenceIndex = 0
    prach.PreambleIndex = 0
    prach.RestrictedSet = "UnrestrictedSet"
    prach.ZeroCorrelationZone = 0
    prach.NPRACHSlot = 11  # the only active slot for ConfigurationIndex=0/FDD/FR1
    return carrier, prach


def test_nrPRACH_matches_matlab_reference():
    carrier, prach = _active_config()
    sym, info = nrPRACH(carrier, prach)

    assert np.allclose(sym, prach_cfg0_seq_ref, atol=1e-6)
    assert info["RootSequence"] == 129
    assert info["CyclicShift"] == 0


def test_nrPRACH_inactive_slot_returns_empty():
    carrier, prach = _active_config()
    prach.NPRACHSlot = 0  # not active for this ConfigurationIndex

    sym, info = nrPRACH(carrier, prach)
    assert sym.shape == (0,)
    assert info["RootSequence"] is None


def test_nrPRACH_root_sequence_table_spot_checks():
    carrier, prach = _active_config()
    for idx, expected in [
        (0, 129),
        (1, 710),
        (2, 140),
        (3, 699),
        (4, 120),
        (5, 719),
        (100, 118),
        (200, 216),
        (500, 354),
        (837, 610),
    ]:
        prach.SequenceIndex = idx
        _, info = nrPRACH(carrier, prach)
        assert info["RootSequence"] == expected


def test_nrPRACH_formats_1_and_2_round_trip_lengths():
    # Format 1 (ConfigurationIndex=28) and Format 2 (ConfigurationIndex=53) repeat the
    # base 839-sample sequence PRACHDuration times (2 and 4 respectively).
    carrier = nrCarrierConfig()
    for configurationIndex, nprachslot, expectedLen, expectedRoot in [
        (28, 3, 839 * 2, 699),
        (53, 2, 839 * 4, 699),
    ]:
        prach = nrPRACHConfig()
        prach.ConfigurationIndex = configurationIndex
        prach.SequenceIndex = 3
        prach.ZeroCorrelationZone = 2
        prach.NPRACHSlot = nprachslot

        sym, info = nrPRACH(carrier, prach)
        assert sym.shape == (expectedLen,)
        assert info["RootSequence"] == expectedRoot


def test_nrPRACH_restricted_set_not_implemented():
    carrier, prach = _active_config()
    prach.RestrictedSet = "RestrictedSetTypeA"
    with pytest.raises(NotImplementedError):
        nrPRACH(carrier, prach)


def test_nrPRACH_format3_not_implemented():
    carrier = nrCarrierConfig()
    prach = nrPRACHConfig()
    prach.ConfigurationIndex = 60  # Format 3
    with pytest.raises(NotImplementedError):
        nrPRACH(carrier, prach)


def test_nrPRACH_invalid_configuration_index_asserts():
    prach = nrPRACHConfig()
    with pytest.raises(AssertionError):
        prach.ConfigurationIndex = 999
