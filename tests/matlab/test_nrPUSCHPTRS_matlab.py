import os

import matlab.engine
import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrPUSCHConfig, nrPUSCHPTRS, nrPUSCHPTRSIndices


def run_nr_puschptrs(cfg, eng):
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = cfg["SubcarrierSpacing"]
    carrier.NSizeGrid = cfg["NSizeGrid"]
    carrier.NStartGrid = cfg["NStartGrid"]
    carrier.NSlot = cfg["NSlot"]

    pusch = nrPUSCHConfig()
    pusch.PRBSet = cfg["PRBSet"]
    pusch.SymbolAllocation = cfg["SymbolAllocation"]
    pusch.RNTI = cfg["RNTI"]
    pusch.DMRS.DMRSTypeAPosition = cfg["DMRSTypeAPosition"]
    pusch.DMRS.DMRSAdditionalPosition = cfg["DMRSAdditionalPosition"]
    pusch.EnablePTRS = bool(cfg["EnablePTRS"])
    pusch.PTRS.TimeDensity = cfg["PTRSTimeDensity"]
    pusch.PTRS.FrequencyDensity = cfg["PTRSFrequencyDensity"]
    pusch.PTRS.REOffset = cfg["PTRSREOffset"]

    sym = nrPUSCHPTRS(carrier, pusch)
    ind = nrPUSCHPTRSIndices(carrier, pusch)

    sym_ref, ind_ref = eng.gen_puschptrs(cfg, nargout=2)
    sym_ref = np.asarray(sym_ref).ravel()
    ind_ref = np.asarray(ind_ref).ravel().astype(int) - 1

    assert sym.shape == sym_ref.shape
    assert np.allclose(sym, sym_ref, atol=1e-6)
    assert ind.shape == ind_ref.shape
    assert np.array_equal(ind, ind_ref)


def _base_cfg():
    return {
        "SubcarrierSpacing": 15,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 0,
        "PRBSet": list(range(52)),
        "SymbolAllocation": [0, 14],
        "RNTI": 1,
        "DMRSTypeAPosition": 2,
        "DMRSAdditionalPosition": 0,
        "EnablePTRS": 1,
        "PTRSTimeDensity": 1,
        "PTRSFrequencyDensity": 2,
        "PTRSREOffset": "00",
    }


def test_nr_puschptrs_default_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    run_nr_puschptrs(_base_cfg(), eng)


@pytest.mark.parametrize("time_density", [1, 2, 4])
@pytest.mark.parametrize("freq_density", [2, 4])
@pytest.mark.parametrize("re_offset", ["00", "01", "10", "11"])
def test_nr_puschptrs_densities_matlab(time_density, freq_density, re_offset, eng):
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["SubcarrierSpacing"] = 30
    cfg["NSizeGrid"] = 106
    cfg["NSlot"] = 5
    cfg["PRBSet"] = list(range(10, 41))
    cfg["RNTI"] = 37
    cfg["PTRSTimeDensity"] = time_density
    cfg["PTRSFrequencyDensity"] = freq_density
    cfg["PTRSREOffset"] = re_offset
    run_nr_puschptrs(cfg, eng)


@pytest.mark.parametrize("typeA_pos", [2, 3])
@pytest.mark.parametrize("add_pos", [0, 1, 2, 3])
def test_nr_puschptrs_dmrs_position_matlab(typeA_pos, add_pos, eng):
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["PRBSet"] = list(range(20))
    cfg["DMRSTypeAPosition"] = typeA_pos
    cfg["DMRSAdditionalPosition"] = add_pos
    cfg["PTRSTimeDensity"] = 4
    cfg["PTRSFrequencyDensity"] = 2
    cfg["PTRSREOffset"] = "01"
    run_nr_puschptrs(cfg, eng)


def test_nr_puschptrs_disabled_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["EnablePTRS"] = 0
    run_nr_puschptrs(cfg, eng)
