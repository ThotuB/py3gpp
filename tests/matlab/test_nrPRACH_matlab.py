import os

import matlab.engine
import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrPRACH, nrPRACHConfig, nrPRACHIndices, nrPRACHOFDMInfo


def run_nr_prach(cfg, eng):
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = cfg["CarrierSubcarrierSpacing"]
    carrier.NSizeGrid = cfg["NSizeGrid"]
    carrier.NStartGrid = cfg["NStartGrid"]

    prach = nrPRACHConfig()
    prach.FrequencyRange = cfg["FrequencyRange"]
    prach.DuplexMode = cfg["DuplexMode"]
    prach.ConfigurationIndex = cfg["ConfigurationIndex"]
    prach.SequenceIndex = cfg["SequenceIndex"]
    prach.PreambleIndex = cfg["PreambleIndex"]
    prach.RestrictedSet = cfg["RestrictedSet"]
    prach.ZeroCorrelationZone = cfg["ZeroCorrelationZone"]
    prach.NPRACHSlot = cfg["NPRACHSlot"]
    prach.RBOffset = cfg["RBOffset"]
    prach.FrequencyStart = cfg["FrequencyStart"]
    prach.FrequencyIndex = cfg["FrequencyIndex"]

    sym, _ = nrPRACH(carrier, prach)
    ind = nrPRACHIndices(carrier, prach)

    sym_ref, ind_ref, nfft_ref, fs_ref = eng.gen_prach(cfg, nargout=4)
    sym_ref = np.asarray(sym_ref).ravel()
    ind_ref = np.asarray(ind_ref).ravel().astype(int) - 1

    assert sym.shape == sym_ref.shape
    assert np.allclose(sym, sym_ref, atol=1e-6)
    assert ind.shape == ind_ref.shape
    assert np.array_equal(ind, ind_ref)

    if prach.Format == "0":
        ofdm_info = nrPRACHOFDMInfo(carrier, prach)
        assert ofdm_info["Nfft"] == int(nfft_ref)
        assert np.isclose(ofdm_info["SampleRate"], fs_ref)


def _base_cfg():
    return {
        "CarrierSubcarrierSpacing": 15,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "FrequencyRange": "FR1",
        "DuplexMode": "FDD",
        "ConfigurationIndex": 0,
        "SequenceIndex": 0,
        "PreambleIndex": 0,
        "RestrictedSet": "UnrestrictedSet",
        "ZeroCorrelationZone": 0,
        "NPRACHSlot": 11,
        "RBOffset": 0,
        "FrequencyStart": 0,
        "FrequencyIndex": 0,
    }


@pytest.mark.parametrize(
    "configuration_index, nprach_slot",
    [(0, 11), (28, 3), (53, 2)],
    ids=["format0", "format1", "format2"],
)
def test_nr_prach_formats_matlab(configuration_index, nprach_slot, eng):
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["ConfigurationIndex"] = configuration_index
    cfg["NPRACHSlot"] = nprach_slot
    run_nr_prach(cfg, eng)


@pytest.mark.parametrize("preamble_index", [0, 7, 30, 63])
@pytest.mark.parametrize("sequence_index", [0, 10, 100])
def test_nr_prach_preamble_sweep_matlab(preamble_index, sequence_index, eng):
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["PreambleIndex"] = preamble_index
    cfg["SequenceIndex"] = sequence_index
    run_nr_prach(cfg, eng)


@pytest.mark.parametrize("zero_correlation_zone", [0, 5, 10, 15])
def test_nr_prach_zero_correlation_zone_matlab(zero_correlation_zone, eng):
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["ZeroCorrelationZone"] = zero_correlation_zone
    run_nr_prach(cfg, eng)


def test_nr_prach_inactive_slot_is_empty_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["NPRACHSlot"] = 0
    run_nr_prach(cfg, eng)
