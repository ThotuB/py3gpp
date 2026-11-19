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


def _symbols_from_indices(indices, carrier, pusch):
    frame_size = (carrier.NStartGrid if not pusch.NRBSize else pusch.NRBSize) * (
        carrier.NSizeGrid if pusch.NSizeBWP is None else pusch.NSizeBWP
    )
    return sorted(set((indices // frame_size).tolist()))


def test_nrPUSCHDMRS_typeB_anchors_to_allocation_start_not_slot():
    # Regression test: Type A anchors its DM-RS position to a fixed slot-absolute symbol
    # regardless of where SymbolAllocation starts -- wrong for a late-starting allocation (e.g. a
    # TDD Special slot's uplink tail). Type B anchors to the allocation's own first symbol
    # instead (TS 38.211 Table 6.4.1.1.3-3), so the DM-RS must land inside the allocation.
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52
    pusch = nrPUSCHConfig()
    pusch.PRBSet = list(range(52))
    pusch.MappingType = "B"
    pusch.SymbolAllocation = [12, 2]  # a 2-symbol UL tail, e.g. symbols 12-13 of the slot

    indices = nrPUSCHDMRSIndices(carrier, pusch)
    syms = _symbols_from_indices(indices, carrier, pusch)
    assert syms == [12]  # base position 0 (Table 6.4.1.1.3-3, duration=2) + SymbolAllocation[0]


def test_nrPUSCHDMRS_typeB_additional_position_matches_table():
    # TS 38.211 Table 6.4.1.1.3-3: duration=9, additional position 2 -> base [0, 3, 6].
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52
    pusch = nrPUSCHConfig()
    pusch.PRBSet = list(range(52))
    pusch.MappingType = "B"
    pusch.SymbolAllocation = [5, 9]
    pusch.DMRS.DMRSAdditionalPosition = 2

    indices = nrPUSCHDMRSIndices(carrier, pusch)
    syms = _symbols_from_indices(indices, carrier, pusch)
    assert syms == [5, 8, 11]


def test_nrPUSCHDMRS_typeB_double_symbol_matches_table():
    # TS 38.211 Table 6.4.1.1.3-4: duration=8, additional position 1 -> base [0, 5], each
    # expanded into a symbol pair -> [0, 1, 5, 6].
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52
    pusch = nrPUSCHConfig()
    pusch.PRBSet = list(range(52))
    pusch.MappingType = "B"
    pusch.SymbolAllocation = [0, 8]
    pusch.DMRS.DMRSLength = 2
    pusch.DMRS.DMRSAdditionalPosition = 1

    indices = nrPUSCHDMRSIndices(carrier, pusch)
    syms = _symbols_from_indices(indices, carrier, pusch)
    assert syms == [0, 1, 5, 6]
