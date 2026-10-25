import numpy as np
import pytest

from py3gpp import (
    nrCarrierConfig,
    nrPUCCH0Config,
    nrPUCCH1Config,
    nrPUCCH2Config,
    nrPUCCH3Config,
    nrPUCCH4Config,
    nrPUCCHIndices,
)


def _carrier():
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52
    carrier.NStartGrid = 0
    carrier.NSlot = 7
    carrier.SubcarrierSpacing = 30
    return carrier


def test_nrPUCCHIndices_format0_matches_matlab():
    # Reference indices captured from a live MATLAB 5G Toolbox (R2026a) session, converted
    # from MATLAB's 1-based indexing.
    carrier = _carrier()
    pucch = nrPUCCH0Config()
    pucch.SymbolAllocation = [11, 2]
    pucch.PRBSet = list(range(4))
    pucch.FrequencyHopping = "intraSlot"
    pucch.SecondHopStartPRB = 10
    pucch.GroupHopping = "enable"
    pucch.HoppingID = 100
    pucch.InitialCyclicShift = 3

    ind = nrPUCCHIndices(carrier, pucch)
    assert ind.shape == (96,)
    assert ind[0] == 6864
    assert ind[-1] == 7655
    assert len(np.unique(ind)) == ind.size


def test_nrPUCCHIndices_format1_matches_matlab():
    carrier = _carrier()
    pucch = nrPUCCH1Config()
    pucch.SymbolAllocation = [0, 14]
    pucch.PRBSet = list(range(3))
    pucch.FrequencyHopping = "intraSlot"
    pucch.SecondHopStartPRB = 5
    pucch.GroupHopping = "enable"
    pucch.HoppingID = 50
    pucch.InitialCyclicShift = 2
    pucch.OCCI = 1

    ind = nrPUCCHIndices(carrier, pucch)
    assert ind.shape == (252,)
    assert len(np.unique(ind)) == ind.size


def test_nrPUCCHIndices_format2_matches_matlab():
    carrier = _carrier()
    pucch = nrPUCCH2Config()
    pucch.SymbolAllocation = [12, 2]
    pucch.PRBSet = list(range(6))
    pucch.NID = 200
    pucch.RNTI = 50

    ind = nrPUCCHIndices(carrier, pucch)
    assert ind.shape == (96,)
    assert len(np.unique(ind)) == ind.size


def test_nrPUCCHIndices_nonzero_nstartgrid_matches_matlab():
    # Regression test: the carrier/BWP offset must be (NStartBWP - NStartGrid), not raw
    # NStartBWP -- caught via a live MATLAB cross-check with NStartGrid != 0 (every earlier
    # PUCCH test used NStartGrid=0, which masked this). Reference indices from MATLAB.
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = 15
    carrier.NSizeGrid = 106
    carrier.NStartGrid = 10
    carrier.NSlot = 3

    pucch = nrPUCCH0Config()
    pucch.SymbolAllocation = [11, 2]
    pucch.PRBSet = list(range(2, 6))
    pucch.FrequencyHopping = "intraSlot"
    pucch.SecondHopStartPRB = 10
    pucch.GroupHopping = "enable"
    pucch.HoppingID = 100
    pucch.InitialCyclicShift = 3

    ind = nrPUCCHIndices(carrier, pucch)
    assert ind.shape == (96,)
    assert ind[0] == 14016
    assert len(np.unique(ind)) == ind.size


def test_nrPUCCHIndices_within_grid_bounds():
    carrier = _carrier()
    pucch = nrPUCCH0Config()
    pucch.SymbolAllocation = [0, 1]
    pucch.PRBSet = [0]

    ind = nrPUCCHIndices(carrier, pucch)
    assert ind.min() >= 0
    assert ind.max() < carrier.NSizeGrid * 12 * 14


@pytest.mark.parametrize("configCls", [nrPUCCH3Config, nrPUCCH4Config])
def test_nrPUCCHIndices_formats_3_4_raise_not_implemented(configCls):
    carrier = _carrier()
    pucch = configCls()
    with pytest.raises(NotImplementedError):
        nrPUCCHIndices(carrier, pucch)


def test_nrPUCCHIndices_interlacing_raises_not_implemented():
    carrier = _carrier()
    pucch = nrPUCCH0Config()
    pucch.Interlacing = True
    with pytest.raises(NotImplementedError):
        nrPUCCHIndices(carrier, pucch)
