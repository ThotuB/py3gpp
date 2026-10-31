import numpy as np

from py3gpp import nrCarrierConfig, nrPDSCHConfig, nrPDSCHIndices, nrPDSCHReservedConfig


def _carrier():
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = 30
    carrier.NSizeGrid = 52
    carrier.NStartGrid = 0
    # NSlot=0 so that an unperiodic SymbolSet given in local 0..SymbolsPerSlot-1 terms lines up
    # and actually applies -- see test_reservation_period_projects_onto_current_slot for the
    # NSlot/Period interaction itself.
    carrier.NSlot = 0
    return carrier


def _pdsch():
    pdsch = nrPDSCHConfig()
    pdsch.PRBSet = list(range(52))
    pdsch.SymbolAllocation = [0, 14]
    return pdsch


def test_no_reservation_matches_plain_indices():
    carrier = _carrier()
    pdsch = _pdsch()
    plain = nrPDSCHIndices(carrier, pdsch)

    pdsch.ReservedPRB = []
    reserved = nrPDSCHIndices(carrier, pdsch)

    assert np.array_equal(np.sort(plain), np.sort(reserved))


def test_reservation_excludes_prbs():
    carrier = _carrier()
    pdsch = _pdsch()

    rsv = nrPDSCHReservedConfig()
    rsv.PRBSet = list(range(10, 15))
    rsv.SymbolSet = list(range(14))
    pdsch.ReservedPRB = [rsv]

    ind = nrPDSCHIndices(carrier, pdsch)
    full = nrCarrierConfig()
    full.SubcarrierSpacing = 30
    full.NSizeGrid = 52

    # None of the reserved PRBs' subcarriers should appear in any occupied symbol.
    totalSC = carrier.NSizeGrid * pdsch.NRBSize
    for prb in range(10, 15):
        reserved_sc = np.arange(prb * pdsch.NRBSize, (prb + 1) * pdsch.NRBSize)
        for sym in range(14):
            if sym == 2:  # default DM-RS symbol, already excluded regardless
                continue
            assert not np.any(np.isin(ind, reserved_sc + sym * totalSC))


def test_reservation_symbol_subset_only_excludes_those_symbols():
    carrier = _carrier()
    pdsch = _pdsch()

    rsv = nrPDSCHReservedConfig()
    rsv.PRBSet = [20]
    rsv.SymbolSet = [5]
    pdsch.ReservedPRB = [rsv]

    ind = nrPDSCHIndices(carrier, pdsch)
    totalSC = carrier.NSizeGrid * pdsch.NRBSize
    reserved_sc = np.arange(20 * pdsch.NRBSize, 21 * pdsch.NRBSize)

    assert not np.any(np.isin(ind, reserved_sc + 5 * totalSC))
    # Symbol 6 (not in the reservation's SymbolSet) must keep its RBs intact.
    assert np.all(np.isin(reserved_sc + 6 * totalSC, ind))


def test_reservation_outside_channel_prbset_is_noop():
    carrier = _carrier()
    pdsch = _pdsch()
    pdsch.PRBSet = list(range(20))
    plain = nrPDSCHIndices(carrier, pdsch)

    rsv = nrPDSCHReservedConfig()
    rsv.PRBSet = list(range(30, 40))
    rsv.SymbolSet = list(range(14))
    pdsch.ReservedPRB = [rsv]
    reserved = nrPDSCHIndices(carrier, pdsch)

    assert np.array_equal(np.sort(plain), np.sort(reserved))


def test_reservation_period_projects_onto_current_slot():
    carrier = _carrier()
    carrier.NSlot = 7
    pdsch = _pdsch()

    # Period=2 -> this reservation's SymbolSet applies to slot (7 % 2) = 1's local symbol range.
    rsv = nrPDSCHReservedConfig()
    rsv.PRBSet = [25]
    rsv.SymbolSet = list(range(14))  # slot 0's full symbol range
    rsv.Period = 2
    pdsch.ReservedPRB = [rsv]

    ind_slot7 = nrPDSCHIndices(carrier, pdsch)

    carrier0 = _carrier()
    carrier0.NSlot = 0
    rsv0 = nrPDSCHReservedConfig()
    rsv0.PRBSet = [25]
    rsv0.SymbolSet = list(range(14))
    rsv0.Period = 2
    pdsch0 = _pdsch()
    pdsch0.ReservedPRB = [rsv0]
    ind_slot0 = nrPDSCHIndices(carrier0, pdsch0)

    # Slot 7 % 2 == 1 (not 0), so this slot-0-shaped reservation should NOT apply, while an
    # otherwise-identical call at slot 0 should see the full exclusion.
    totalSC = carrier.NSizeGrid * pdsch.NRBSize
    reserved_sc = np.arange(25 * pdsch.NRBSize, 26 * pdsch.NRBSize)
    assert np.all(np.isin(reserved_sc + 0 * totalSC, ind_slot7))
    assert not np.any(np.isin(ind_slot0, reserved_sc + 0 * totalSC))
