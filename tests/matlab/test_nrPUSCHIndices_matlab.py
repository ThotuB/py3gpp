import os

import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrPUSCHConfig, nrPUSCHIndices


def run_nr_puschindices(cfg, eng):
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = cfg["SubcarrierSpacing"]
    carrier.NSizeGrid = cfg["NSizeGrid"]
    carrier.NStartGrid = cfg["NStartGrid"]
    carrier.NSlot = cfg["NSlot"]

    pusch = nrPUSCHConfig()
    pusch.PRBSet = cfg["PRBSet"]
    pusch.SymbolAllocation = cfg["SymbolAllocation"]
    pusch.DMRS.DMRSTypeAPosition = cfg["DMRSTypeAPosition"]
    pusch.DMRS.DMRSAdditionalPosition = cfg["DMRSAdditionalPosition"]
    pusch.DMRS.DMRSConfigurationType = cfg["DMRSConfigurationType"]

    ind = nrPUSCHIndices(carrier, pusch)

    ind_ref = eng.gen_puschindices(cfg)
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


def test_nr_puschindices_default_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    run_nr_puschindices(_base_cfg(), eng)


@pytest.mark.parametrize("sym_start,num_syms", [(2, 12), (3, 11), (1, 13)])
def test_nr_puschindices_nonzero_symstart_matlab(sym_start, num_syms, eng):
    # Regression test: nrPUSCHIndices must use occupied_syms = [symStart, symStart+numSyms),
    # not [symStart, numSyms) -- see the matching nrPDSCHIndices regression test for details.
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["SymbolAllocation"] = [sym_start, num_syms]
    run_nr_puschindices(cfg, eng)
