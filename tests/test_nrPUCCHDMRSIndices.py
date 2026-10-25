import numpy as np
import pytest

from py3gpp import (
    nrCarrierConfig,
    nrPUCCH0Config,
    nrPUCCH1Config,
    nrPUCCH2Config,
    nrPUCCH3Config,
    nrPUCCH4Config,
    nrPUCCHDMRSIndices,
)


def _carrier():
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = 30
    carrier.NSizeGrid = 52
    carrier.NStartGrid = 0
    carrier.NSlot = 7
    return carrier


def test_nrPUCCHDMRSIndices_format0_is_empty():
    carrier = _carrier()
    pucch = nrPUCCH0Config()
    ind = nrPUCCHDMRSIndices(carrier, pucch)
    assert ind.shape == (0,)


def test_nrPUCCHDMRSIndices_format1_matches_matlab():
    # Reference indices captured from a live MATLAB 5G Toolbox (R2026a) session, converted
    # from MATLAB's 1-based indexing.
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

    ind = nrPUCCHDMRSIndices(carrier, pucch)
    assert ind.shape == (252,)
    assert ind[0] == 0
    assert ind[-1] == 7583
    assert len(np.unique(ind)) == ind.size


def test_nrPUCCHDMRSIndices_format2_matches_matlab():
    carrier = _carrier()
    pucch = nrPUCCH2Config()
    pucch.PRBSet = list(range(6))
    pucch.SymbolAllocation = [12, 2]
    pucch.FrequencyHopping = "intraSlot"
    pucch.SecondHopStartPRB = 20
    pucch.NID0 = 300

    ind = nrPUCCHDMRSIndices(carrier, pucch)
    assert ind.shape == (48,)
    assert ind[0] == 7489
    assert ind[-1] == 8422
    assert len(np.unique(ind)) == ind.size


def test_nrPUCCHDMRSIndices_format2_single_symbol_matches_matlab():
    carrier = _carrier()
    pucch = nrPUCCH2Config()
    pucch.PRBSet = list(range(4))
    pucch.SymbolAllocation = [13, 1]
    pucch.NID0 = 42

    ind = nrPUCCHDMRSIndices(carrier, pucch)
    assert ind.shape == (16,)
    assert ind[0] == 8113
    assert ind[-1] == 8158


def test_nrPUCCHDMRSIndices_format3_matches_matlab():
    carrier = _carrier()
    pucch = nrPUCCH3Config()
    pucch.PRBSet = list(range(12))
    pucch.SymbolAllocation = [0, 10]
    pucch.FrequencyHopping = "intraSlot"
    pucch.SecondHopStartPRB = 15
    pucch.GroupHopping = "enable"
    pucch.HoppingID = 77
    pucch.AdditionalDMRS = True

    ind = nrPUCCHDMRSIndices(carrier, pucch)
    assert ind.shape == (576,)
    assert ind[0] == 624
    assert ind[-1] == 5315
    assert len(np.unique(ind)) == ind.size


def test_nrPUCCHDMRSIndices_format3_no_hopping_no_additional_matches_matlab():
    carrier = _carrier()
    pucch = nrPUCCH3Config()
    pucch.PRBSet = list(range(4))
    pucch.SymbolAllocation = [2, 7]
    pucch.AdditionalDMRS = False

    ind = nrPUCCHDMRSIndices(carrier, pucch)
    assert ind.shape == (96,)
    assert ind[0] == 1872
    assert ind[-1] == 3791


def test_nrPUCCHDMRSIndices_format4_matches_matlab():
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

    ind = nrPUCCHDMRSIndices(carrier, pucch)
    assert ind.shape == (96,)
    assert ind[0] == 624
    assert ind[-1] == 7607
    assert len(np.unique(ind)) == ind.size


def test_nrPUCCHDMRSIndices_nonzero_nstartgrid_matches_matlab():
    # Regression test for the same carrier/BWP offset bug fixed in nrPUCCHIndices: the offset
    # must be (NStartBWP - NStartGrid), not raw NStartBWP.
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = 15
    carrier.NSizeGrid = 106
    carrier.NStartGrid = 10
    carrier.NSlot = 3
    carrier.CyclicPrefix = "normal"

    pucch = nrPUCCH1Config()
    pucch.PRBSet = list(range(2, 5))
    pucch.SymbolAllocation = [3, 9]
    pucch.FrequencyHopping = "neither"
    pucch.GroupHopping = "enable"
    pucch.HoppingID = 20
    pucch.OCCI = 0

    ind = nrPUCCHDMRSIndices(carrier, pucch)
    assert ind.shape == (180,)
    assert ind[0] == 3840
    assert ind[-1] == 14051


@pytest.mark.parametrize("configCls", [nrPUCCH1Config, nrPUCCH2Config])
def test_nrPUCCHDMRSIndices_interlacing_raises_not_implemented(configCls):
    carrier = _carrier()
    pucch = configCls()
    pucch.Interlacing = True
    with pytest.raises(NotImplementedError):
        nrPUCCHDMRSIndices(carrier, pucch)


def test_nrPUCCHDMRSIndices_R16_flag_does_not_affect_positions():
    # DM-RS RE positions are independent of DMRSUplinkTransformPrecodingR16 -- only the
    # sequence VALUES differ (and that path raises NotImplementedError in nrPUCCHDMRS).
    carrier = _carrier()
    pucch = nrPUCCH3Config()
    pucch.PRBSet = list(range(4))
    pucch.SymbolAllocation = [2, 7]

    indBase = nrPUCCHDMRSIndices(carrier, pucch)
    pucch.DMRSUplinkTransformPrecodingR16 = True
    indR16 = nrPUCCHDMRSIndices(carrier, pucch)
    assert np.array_equal(indBase, indR16)
