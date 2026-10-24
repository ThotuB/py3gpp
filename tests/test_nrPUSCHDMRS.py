import numpy as np

from py3gpp import nrCarrierConfig, nrPUSCHConfig, nrPUSCHDMRS, nrPUSCHDMRSIndices


def _carrier_and_cfg():
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52
    pusch = nrPUSCHConfig()
    pusch.PRBSet = list(range(52))
    pusch.SymbolAllocation = [0, 14]
    return carrier, pusch


def test_nrPUSCHDMRS_shape_matches_indices():
    carrier, pusch = _carrier_and_cfg()
    indices = nrPUSCHDMRSIndices(carrier, pusch)
    syms = nrPUSCHDMRS(pusch, carrier)

    assert syms.shape == indices.shape
    assert len(np.unique(indices)) == indices.size
    assert np.allclose(np.abs(syms), 1.0)  # unit-magnitude QPSK


def test_nrPUSCHDMRS_deterministic():
    carrier, pusch = _carrier_and_cfg()
    syms1 = nrPUSCHDMRS(pusch, carrier)
    syms2 = nrPUSCHDMRS(pusch, carrier)
    assert np.array_equal(syms1, syms2)


def test_nrPUSCHDMRS_nscid_changes_sequence():
    carrier, pusch = _carrier_and_cfg()
    syms_scid0 = nrPUSCHDMRS(pusch, carrier)
    pusch.DMRS.NSCID = 1
    syms_scid1 = nrPUSCHDMRS(pusch, carrier)
    assert not np.array_equal(syms_scid0, syms_scid1)


def test_nrPUSCHDMRS_additional_position_adds_symbols():
    carrier, pusch = _carrier_and_cfg()
    base_indices = nrPUSCHDMRSIndices(carrier, pusch)
    pusch.DMRS.DMRSAdditionalPosition = 2
    more_indices = nrPUSCHDMRSIndices(carrier, pusch)
    assert more_indices.size > base_indices.size
