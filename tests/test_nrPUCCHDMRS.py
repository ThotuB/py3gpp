import numpy as np
import pytest

from py3gpp import (
    nrCarrierConfig,
    nrPUCCH0Config,
    nrPUCCH1Config,
    nrPUCCH2Config,
    nrPUCCH3Config,
    nrPUCCH4Config,
    nrPUCCHDMRS,
)


def _carrier():
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = 30
    carrier.NSizeGrid = 52
    carrier.NStartGrid = 0
    carrier.NSlot = 7
    return carrier


def test_nrPUCCHDMRS_format0_is_empty():
    carrier = _carrier()
    pucch = nrPUCCH0Config()
    sym = nrPUCCHDMRS(carrier, pucch)
    assert sym.shape == (0,)


def test_nrPUCCHDMRS_format1_matches_matlab():
    # Reference values captured from a live MATLAB 5G Toolbox (R2026a) session.
    carrier = _carrier()
    pucch = nrPUCCH1Config()
    pucch.PRBSet = list(range(3))
    pucch.SymbolAllocation = [0, 14]
    pucch.FrequencyHopping = "intraSlot"
    pucch.SecondHopStartPRB = 5
    pucch.GroupHopping = "enable"
    pucch.HoppingID = 50
    pucch.InitialCyclicShift = 2
    pucch.OCCI = 1

    sym = nrPUCCHDMRS(carrier, pucch)
    assert sym.shape == (252,)
    assert np.allclose(np.abs(sym), 1.0)
    assert np.allclose(sym[:3], [1.0 + 0.0j, 0.514555 + 0.857457j, 0.839589 - 0.543222j], atol=1e-6)


def test_nrPUCCHDMRS_format2_matches_matlab():
    carrier = _carrier()
    pucch = nrPUCCH2Config()
    pucch.PRBSet = list(range(6))
    pucch.SymbolAllocation = [12, 2]
    pucch.FrequencyHopping = "intraSlot"
    pucch.SecondHopStartPRB = 20
    pucch.NID0 = 300

    sym = nrPUCCHDMRS(carrier, pucch)
    assert sym.shape == (48,)
    assert np.allclose(np.abs(sym), 1.0)
    assert np.allclose(sym[:3], [0.707107 + 0.707107j, 0.707107 - 0.707107j, -0.707107 + 0.707107j], atol=1e-6)


def test_nrPUCCHDMRS_format2_single_symbol_matches_matlab():
    carrier = _carrier()
    pucch = nrPUCCH2Config()
    pucch.PRBSet = list(range(4))
    pucch.SymbolAllocation = [13, 1]
    pucch.NID0 = 42

    sym = nrPUCCHDMRS(carrier, pucch)
    assert sym.shape == (16,)
    assert np.allclose(sym[:3], [-0.707107 - 0.707107j, 0.707107 - 0.707107j, 0.707107 - 0.707107j], atol=1e-6)


def test_nrPUCCHDMRS_format3_matches_matlab():
    carrier = _carrier()
    pucch = nrPUCCH3Config()
    pucch.PRBSet = list(range(12))
    pucch.SymbolAllocation = [0, 10]
    pucch.FrequencyHopping = "intraSlot"
    pucch.SecondHopStartPRB = 15
    pucch.GroupHopping = "enable"
    pucch.HoppingID = 77
    pucch.AdditionalDMRS = True

    sym = nrPUCCHDMRS(carrier, pucch)
    assert sym.shape == (576,)
    assert np.allclose(np.abs(sym), 1.0)
    assert np.allclose(sym[:3], [1.0 + 0.0j, 0.496734 - 0.867903j, 0.0113 + 0.999936j], atol=1e-5)


def test_nrPUCCHDMRS_format3_no_hopping_no_additional_matches_matlab():
    carrier = _carrier()
    pucch = nrPUCCH3Config()
    pucch.PRBSet = list(range(4))
    pucch.SymbolAllocation = [2, 7]
    pucch.AdditionalDMRS = False

    sym = nrPUCCHDMRS(carrier, pucch)
    assert sym.shape == (96,)
    assert np.allclose(sym[:3], [1.0 + 0.0j, -0.992501 - 0.122238j, 0.987862 - 0.155334j], atol=1e-5)


def test_nrPUCCHDMRS_format4_matches_matlab():
    carrier = _carrier()
    pucch = nrPUCCH4Config()
    pucch.PRBSet = list(range(2))
    pucch.SymbolAllocation = [0, 14]
    pucch.FrequencyHopping = "intraSlot"
    pucch.SecondHopStartPRB = 8
    pucch.GroupHopping = "enable"
    pucch.HoppingID = 99
    pucch.SpreadingFactor = 4
    pucch.OCCI = 2
    pucch.AdditionalDMRS = True

    sym = nrPUCCHDMRS(carrier, pucch)
    assert sym.shape == (96,)
    assert np.allclose(np.abs(sym), 1.0)
    assert np.allclose(sym[:3], [-0.707107 - 0.707107j, -0.965926 + 0.258819j, -0.965926 - 0.258819j], atol=1e-6)


@pytest.mark.parametrize("configCls", [nrPUCCH1Config, nrPUCCH2Config])
def test_nrPUCCHDMRS_interlacing_raises_not_implemented(configCls):
    carrier = _carrier()
    pucch = configCls()
    pucch.Interlacing = True
    with pytest.raises(NotImplementedError):
        nrPUCCHDMRS(carrier, pucch)


@pytest.mark.parametrize("configCls", [nrPUCCH3Config, nrPUCCH4Config])
def test_nrPUCCHDMRS_R16_transform_precoding_raises_not_implemented(configCls):
    carrier = _carrier()
    pucch = configCls()
    pucch.DMRSUplinkTransformPrecodingR16 = True
    pucch.Modulation = "pi/2-BPSK"
    with pytest.raises(NotImplementedError):
        nrPUCCHDMRS(carrier, pucch)
