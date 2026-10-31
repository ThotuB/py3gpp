import os

import matlab.engine
from matlab.engine.matlabengine import MatlabEngine
import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrPRS, nrPRSConfig, nrPRSIndices


def run_nr_prs(cfg, eng):
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = cfg["SubcarrierSpacing"]
    carrier.NSizeGrid = cfg["NSizeGrid"]
    carrier.NStartGrid = cfg["NStartGrid"]
    carrier.NSlot = cfg["NSlot"]

    prs = nrPRSConfig()
    prs.PRSResourceSetPeriod = cfg["PRSResourceSetPeriod"]
    prs.PRSResourceOffset = cfg["PRSResourceOffset"]
    prs.PRSResourceRepetition = cfg["PRSResourceRepetition"]
    prs.PRSResourceTimeGap = cfg["PRSResourceTimeGap"]
    prs.MutingPattern1 = cfg["MutingPattern1"]
    prs.MutingBitRepetition = cfg["MutingBitRepetition"]
    prs.MutingPattern2 = cfg["MutingPattern2"]
    prs.NumPRSSymbols = cfg["NumPRSSymbols"]
    prs.SymbolStart = cfg["SymbolStart"]
    prs.NumRB = cfg["NumRB"]
    prs.RBOffset = cfg["RBOffset"]
    prs.CombSize = cfg["CombSize"]
    prs.REOffset = cfg["REOffset"]
    prs.NPRSID = cfg["NPRSID"]

    sym = nrPRS(carrier, prs)
    ind = nrPRSIndices(carrier, prs)

    sym_ref, ind_ref = eng.gen_prs(cfg, nargout=2)
    sym_ref = np.asarray(sym_ref).ravel()
    ind_ref = np.asarray(ind_ref).ravel().astype(int) - 1

    assert sym.shape == sym_ref.shape
    assert np.allclose(sym, sym_ref, atol=1e-6)
    assert ind.shape == ind_ref.shape
    assert np.array_equal(ind, ind_ref)


@pytest.fixture(scope="session")
def eng():
    eng = matlab.engine.connect_matlab()
    assert isinstance(eng, MatlabEngine)
    yield eng
    eng.quit()


def test_nr_prs_default_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    cfg = {
        "SubcarrierSpacing": 15,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 0,
        "PRSResourceSetPeriod": "on",
        "PRSResourceOffset": 0,
        "PRSResourceRepetition": 1,
        "PRSResourceTimeGap": 1,
        "MutingPattern1": [],
        "MutingBitRepetition": 1,
        "MutingPattern2": [],
        "NumPRSSymbols": 12,
        "SymbolStart": 0,
        "NumRB": 52,
        "RBOffset": 0,
        "CombSize": 2,
        "REOffset": 0,
        "NPRSID": 0,
    }
    run_nr_prs(cfg, eng)


def test_nr_prs_multi_resource_muting_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    cfg = {
        "SubcarrierSpacing": 15,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 0,
        "PRSResourceSetPeriod": [8, 0],
        "PRSResourceOffset": [0, 4],
        "PRSResourceRepetition": 2,
        "PRSResourceTimeGap": 1,
        "MutingPattern1": [1, 1],
        "MutingBitRepetition": 1,
        "MutingPattern2": [1, 0],
        "NumPRSSymbols": [6, 12],
        "SymbolStart": [6, 0],
        "NumRB": 40,
        "RBOffset": 4,
        "CombSize": 4,
        "REOffset": [1, 3],
        "NPRSID": 5,
    }
    run_nr_prs(cfg, eng)


@pytest.mark.parametrize("comb_size", [2, 4, 6, 12])
def test_nr_prs_comb_sizes_matlab(comb_size, eng):
    eng.cd(os.path.dirname(__file__))
    cfg = {
        "SubcarrierSpacing": 15,
        "NSizeGrid": 52,
        "NStartGrid": 10,
        "NSlot": 7,
        "PRSResourceSetPeriod": "on",
        "PRSResourceOffset": 0,
        "PRSResourceRepetition": 1,
        "PRSResourceTimeGap": 1,
        "MutingPattern1": [],
        "MutingBitRepetition": 1,
        "MutingPattern2": [],
        "NumPRSSymbols": 12,
        "SymbolStart": 0,
        "NumRB": 24,
        "RBOffset": 5,
        "CombSize": comb_size,
        "REOffset": comb_size - 1,
        "NPRSID": 200,
    }
    run_nr_prs(cfg, eng)
