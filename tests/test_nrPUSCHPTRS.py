import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrPUSCHConfig, nrPUSCHPTRS


def test_nrPUSCHPTRS_default_matches_matlab():
    # Reference values captured from a live MATLAB 5G Toolbox (R2026a) session.
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52
    pusch = nrPUSCHConfig()
    pusch.PRBSet = list(range(52))
    pusch.SymbolAllocation = [0, 14]
    pusch.EnablePTRS = True

    sym = nrPUSCHPTRS(carrier, pusch)
    assert sym.shape == (338,)
    assert np.allclose(np.abs(sym), 1.0)
    assert np.allclose(sym[:3], [0.707107 - 0.707107j, -0.707107 - 0.707107j, 0.707107 - 0.707107j], atol=1e-6)


def test_nrPUSCHPTRS_nondefault_densities_matches_matlab():
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 106
    carrier.NSlot = 5
    pusch = nrPUSCHConfig()
    pusch.PRBSet = list(range(10, 41))
    pusch.SymbolAllocation = [0, 14]
    pusch.RNTI = 37
    pusch.EnablePTRS = True
    pusch.PTRS.TimeDensity = 2
    pusch.PTRS.FrequencyDensity = 4
    pusch.PTRS.REOffset = "11"

    sym = nrPUSCHPTRS(carrier, pusch)
    assert sym.shape == (48,)
    assert np.allclose(sym[:3], [0.707107 + 0.707107j, -0.707107 - 0.707107j, -0.707107 + 0.707107j], atol=1e-6)


def test_nrPUSCHPTRS_dmrs_typeA_position_matches_matlab():
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52
    pusch = nrPUSCHConfig()
    pusch.PRBSet = list(range(20))
    pusch.SymbolAllocation = [0, 14]
    pusch.DMRS.DMRSTypeAPosition = 3
    pusch.DMRS.DMRSAdditionalPosition = 2
    pusch.EnablePTRS = True
    pusch.PTRS.TimeDensity = 4
    pusch.PTRS.FrequencyDensity = 2
    pusch.PTRS.REOffset = "01"

    sym = nrPUSCHPTRS(carrier, pusch)
    assert sym.shape == (10,)
    assert np.allclose(sym[:3], [-0.707107 - 0.707107j, 0.707107 + 0.707107j, -0.707107 - 0.707107j], atol=1e-6)


def test_nrPUSCHPTRS_disabled_returns_empty():
    carrier = nrCarrierConfig()
    pusch = nrPUSCHConfig()
    pusch.PRBSet = list(range(52))
    pusch.EnablePTRS = False
    sym = nrPUSCHPTRS(carrier, pusch)
    assert sym.shape == (0,)


def test_nrPUSCHPTRS_transform_precoding_raises_not_implemented():
    carrier = nrCarrierConfig()
    pusch = nrPUSCHConfig()
    pusch.PRBSet = list(range(52))
    pusch.EnablePTRS = True
    pusch.TransformPrecoding = "enabled"
    with pytest.raises(NotImplementedError):
        nrPUSCHPTRS(carrier, pusch)
