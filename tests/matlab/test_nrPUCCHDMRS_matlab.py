import os

import matlab.engine
import numpy as np
import pytest

from py3gpp import (
    nrCarrierConfig,
    nrPUCCH1Config,
    nrPUCCH2Config,
    nrPUCCH3Config,
    nrPUCCH4Config,
    nrPUCCHDMRS,
    nrPUCCHDMRSIndices,
)


def run_nr_pucch_dmrs(cfg, pucch, carrier, eng):
    sym = nrPUCCHDMRS(carrier, pucch)
    ind = nrPUCCHDMRSIndices(carrier, pucch)

    sym_ref, ind_ref = eng.gen_pucchdmrs(cfg, nargout=2)
    sym_ref = np.asarray(sym_ref).ravel()
    ind_ref = np.asarray(ind_ref).ravel().astype(int) - 1

    assert sym.shape == sym_ref.shape
    assert np.allclose(sym, sym_ref, atol=1e-6)
    assert ind.shape == ind_ref.shape
    assert np.array_equal(ind, ind_ref)


def _carrier():
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = 30
    carrier.NSizeGrid = 52
    carrier.NStartGrid = 0
    carrier.NSlot = 7
    return carrier


def test_nr_pucch_dmrs_format1_matlab(eng):
    eng.cd(os.path.dirname(__file__))
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

    cfg = {
        "SubcarrierSpacing": 30,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 7,
        "Format": 1,
        "PRBSet": list(range(3)),
        "SymbolAllocation": [0, 14],
        "FrequencyHopping": "intraSlot",
        "SecondHopStartPRB": 5,
        "GroupHopping": "enable",
        "HoppingID": 50,
        "InitialCyclicShift": 2,
        "OCCI": 1,
    }
    run_nr_pucch_dmrs(cfg, pucch, carrier, eng)


def test_nr_pucch_dmrs_format2_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    carrier = _carrier()
    pucch = nrPUCCH2Config()
    pucch.PRBSet = list(range(6))
    pucch.SymbolAllocation = [12, 2]
    pucch.FrequencyHopping = "intraSlot"
    pucch.SecondHopStartPRB = 20
    pucch.NID0 = 300

    cfg = {
        "SubcarrierSpacing": 30,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 7,
        "Format": 2,
        "PRBSet": list(range(6)),
        "SymbolAllocation": [12, 2],
        "FrequencyHopping": "intraSlot",
        "SecondHopStartPRB": 20,
        "NID0": 300,
    }
    run_nr_pucch_dmrs(cfg, pucch, carrier, eng)


def test_nr_pucch_dmrs_format2_single_symbol_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    carrier = _carrier()
    pucch = nrPUCCH2Config()
    pucch.PRBSet = list(range(4))
    pucch.SymbolAllocation = [13, 1]
    pucch.NID0 = 42

    cfg = {
        "SubcarrierSpacing": 30,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 7,
        "Format": 2,
        "PRBSet": list(range(4)),
        "SymbolAllocation": [13, 1],
        "FrequencyHopping": "neither",
        "SecondHopStartPRB": 1,
        "NID0": 42,
    }
    run_nr_pucch_dmrs(cfg, pucch, carrier, eng)


def test_nr_pucch_dmrs_format3_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    carrier = _carrier()
    pucch = nrPUCCH3Config()
    pucch.PRBSet = list(range(12))
    pucch.SymbolAllocation = [0, 10]
    pucch.FrequencyHopping = "intraSlot"
    pucch.SecondHopStartPRB = 15
    pucch.GroupHopping = "enable"
    pucch.HoppingID = 77
    pucch.AdditionalDMRS = True

    cfg = {
        "SubcarrierSpacing": 30,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 7,
        "Format": 3,
        "PRBSet": list(range(12)),
        "SymbolAllocation": [0, 10],
        "FrequencyHopping": "intraSlot",
        "SecondHopStartPRB": 15,
        "GroupHopping": "enable",
        "HoppingID": 77,
        "AdditionalDMRS": True,
    }
    run_nr_pucch_dmrs(cfg, pucch, carrier, eng)


def test_nr_pucch_dmrs_format3_no_hopping_no_additional_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    carrier = _carrier()
    pucch = nrPUCCH3Config()
    pucch.PRBSet = list(range(4))
    pucch.SymbolAllocation = [2, 7]
    pucch.HoppingID = 0
    pucch.AdditionalDMRS = False

    cfg = {
        "SubcarrierSpacing": 30,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 7,
        "Format": 3,
        "PRBSet": list(range(4)),
        "SymbolAllocation": [2, 7],
        "FrequencyHopping": "neither",
        "SecondHopStartPRB": 1,
        "GroupHopping": "neither",
        "HoppingID": 0,
        "AdditionalDMRS": False,
    }
    run_nr_pucch_dmrs(cfg, pucch, carrier, eng)


def test_nr_pucch_dmrs_format4_matlab(eng):
    eng.cd(os.path.dirname(__file__))
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

    cfg = {
        "SubcarrierSpacing": 30,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 7,
        "Format": 4,
        "PRBSet": list(range(2)),
        "SymbolAllocation": [0, 14],
        "FrequencyHopping": "intraSlot",
        "SecondHopStartPRB": 8,
        "GroupHopping": "enable",
        "HoppingID": 99,
        "SpreadingFactor": 4,
        "OCCI": 2,
        "AdditionalDMRS": True,
    }
    run_nr_pucch_dmrs(cfg, pucch, carrier, eng)
