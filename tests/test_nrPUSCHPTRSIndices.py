import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrPUSCHConfig, nrPUSCHPTRSIndices


def test_nrPUSCHPTRSIndices_default_matches_matlab():
    # Reference indices captured from a live MATLAB 5G Toolbox (R2026a) session, converted
    # from MATLAB's 1-based indexing.
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52
    pusch = nrPUSCHConfig()
    pusch.PRBSet = list(range(52))
    pusch.SymbolAllocation = [0, 14]
    pusch.EnablePTRS = True

    ind = nrPUSCHPTRSIndices(carrier, pusch)
    assert ind.shape == (338,)
    assert ind[0] == 12
    assert ind[-1] == 8724
    assert len(np.unique(ind)) == ind.size


def test_nrPUSCHPTRSIndices_nondefault_densities_matches_matlab():
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

    ind = nrPUSCHPTRSIndices(carrier, pusch)
    assert ind.shape == (48,)
    assert ind[0] == 140
    assert ind[-1] == 15740


def test_nrPUSCHPTRSIndices_dmrs_typeA_position_matches_matlab():
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

    ind = nrPUSCHPTRSIndices(carrier, pusch)
    assert ind.shape == (10,)
    assert ind[0] == 14
    assert ind[-1] == 230


def test_nrPUSCHPTRSIndices_disabled_returns_empty():
    carrier = nrCarrierConfig()
    pusch = nrPUSCHConfig()
    pusch.PRBSet = list(range(52))
    pusch.EnablePTRS = False
    ind = nrPUSCHPTRSIndices(carrier, pusch)
    assert ind.shape == (0,)


def test_nrPUSCHPTRSIndices_transform_precoding_raises_not_implemented():
    carrier = nrCarrierConfig()
    pusch = nrPUSCHConfig()
    pusch.PRBSet = list(range(52))
    pusch.EnablePTRS = True
    pusch.TransformPrecoding = "enabled"
    with pytest.raises(NotImplementedError):
        nrPUSCHPTRSIndices(carrier, pusch)
