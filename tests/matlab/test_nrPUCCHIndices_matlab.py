import os

import matlab.engine
import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrPUCCH0Config, nrPUCCH1Config, nrPUCCH2Config, nrPUCCHIndices


def run_nr_pucch_indices(cfg, pucch, carrier, eng):
    ind = nrPUCCHIndices(carrier, pucch)

    ind_ref = eng.gen_pucchindices(cfg)
    ind_ref = np.asarray(ind_ref).ravel().astype(int) - 1

    assert ind.shape == ind_ref.shape
    assert np.array_equal(ind, ind_ref)


def _carrier(nStartGrid=0):
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = 30
    carrier.NSizeGrid = 52
    carrier.NStartGrid = nStartGrid
    carrier.NSlot = 7
    return carrier


def test_nr_pucch_indices_format0_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    carrier = _carrier()
    pucch = nrPUCCH0Config()
    pucch.SymbolAllocation = [11, 2]
    pucch.PRBSet = list(range(4))
    pucch.FrequencyHopping = "intraSlot"
    pucch.SecondHopStartPRB = 10
    pucch.GroupHopping = "enable"
    pucch.HoppingID = 100
    pucch.InitialCyclicShift = 3

    cfg = {
        "SubcarrierSpacing": 30,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 7,
        "Format": 0,
        "SymbolAllocation": [11, 2],
        "PRBSet": list(range(4)),
        "FrequencyHopping": "intraSlot",
        "SecondHopStartPRB": 10,
        "GroupHopping": "enable",
        "HoppingID": 100,
        "InitialCyclicShift": 3,
    }
    run_nr_pucch_indices(cfg, pucch, carrier, eng)


def test_nr_pucch_indices_format1_matlab(eng):
    eng.cd(os.path.dirname(__file__))
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

    cfg = {
        "SubcarrierSpacing": 30,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 7,
        "Format": 1,
        "SymbolAllocation": [0, 14],
        "PRBSet": list(range(3)),
        "FrequencyHopping": "intraSlot",
        "SecondHopStartPRB": 5,
        "GroupHopping": "enable",
        "HoppingID": 50,
        "InitialCyclicShift": 2,
        "OCCI": 1,
    }
    run_nr_pucch_indices(cfg, pucch, carrier, eng)


def test_nr_pucch_indices_format2_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    carrier = _carrier()
    pucch = nrPUCCH2Config()
    pucch.SymbolAllocation = [12, 2]
    pucch.PRBSet = list(range(6))
    pucch.NID = 200
    pucch.RNTI = 50

    cfg = {
        "SubcarrierSpacing": 30,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 7,
        "Format": 2,
        "SymbolAllocation": [12, 2],
        "PRBSet": list(range(6)),
        "FrequencyHopping": "neither",
        "SecondHopStartPRB": 1,
        "NID": 200,
        "RNTI": 50,
    }
    run_nr_pucch_indices(cfg, pucch, carrier, eng)


def test_nr_pucch_indices_nonzero_nstartgrid_matlab(eng):
    eng.cd(os.path.dirname(__file__))
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

    cfg = {
        "SubcarrierSpacing": 15,
        "NSizeGrid": 106,
        "NStartGrid": 10,
        "NSlot": 3,
        "Format": 0,
        "SymbolAllocation": [11, 2],
        "PRBSet": list(range(2, 6)),
        "FrequencyHopping": "intraSlot",
        "SecondHopStartPRB": 10,
        "GroupHopping": "enable",
        "HoppingID": 100,
        "InitialCyclicShift": 3,
    }
    run_nr_pucch_indices(cfg, pucch, carrier, eng)
