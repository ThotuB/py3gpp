import os

import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrPDSCHConfig, nrPDSCHIndices


def run_nr_pdschindices(cfg, eng):
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = cfg["SubcarrierSpacing"]
    carrier.NSizeGrid = cfg["NSizeGrid"]
    carrier.NStartGrid = cfg["NStartGrid"]
    carrier.NSlot = cfg["NSlot"]

    pdsch = nrPDSCHConfig()
    pdsch.PRBSet = cfg["PRBSet"]
    pdsch.SymbolAllocation = cfg["SymbolAllocation"]
    pdsch.DMRS.DMRSTypeAPosition = cfg["DMRSTypeAPosition"]
    pdsch.DMRS.DMRSAdditionalPosition = cfg["DMRSAdditionalPosition"]
    pdsch.DMRS.DMRSConfigurationType = cfg["DMRSConfigurationType"]

    ind = nrPDSCHIndices(carrier, pdsch)

    ind_ref = eng.gen_pdschindices(cfg)
    ind_ref = np.asarray(ind_ref).ravel().astype(int) - 1

    assert ind.shape == ind_ref.shape
    assert np.array_equal(np.sort(ind), np.sort(ind_ref))


def _base_cfg():
    return {
        "SubcarrierSpacing": 30,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 7,
        "PRBSet": list(range(52)),
        "SymbolAllocation": [0, 14],
        "DMRSTypeAPosition": 2,
        "DMRSAdditionalPosition": 0,
        "DMRSConfigurationType": 1,
    }


def test_nr_pdschindices_default_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    run_nr_pdschindices(_base_cfg(), eng)


@pytest.mark.parametrize("sym_start,num_syms", [(2, 12), (3, 11), (1, 13)])
def test_nr_pdschindices_nonzero_symstart_matlab(sym_start, num_syms, eng):
    # Regression test: nrPDSCHIndices must use occupied_syms = [symStart, symStart+numSyms),
    # not [symStart, numSyms) -- the latter silently coincides with the former only when
    # symStart + numSyms == SymbolsPerSlot, which every earlier default-allocation test used.
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["SymbolAllocation"] = [sym_start, num_syms]
    run_nr_pdschindices(cfg, eng)


@pytest.mark.parametrize("add_pos", [0, 1, 2, 3])
def test_nr_pdschindices_nonzero_symstart_add_pos_sweep_matlab(add_pos, eng):
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["SymbolAllocation"] = [2, 12]
    cfg["DMRSAdditionalPosition"] = add_pos
    run_nr_pdschindices(cfg, eng)
