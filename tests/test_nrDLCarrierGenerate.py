import numpy as np

from py3gpp import (
    nrBCH,
    nrCarrierConfig,
    nrCORESETConfig,
    nrDLCarrierConfig,
    nrDLCarrierGenerate,
    nrPBCH,
    nrPBCHDMRS,
    nrPBCHDMRSIndices,
    nrPBCHIndices,
    nrPDCCHConfig,
    nrPSS,
    nrPSSIndices,
    nrSearchSpaceConfig,
    nrSSBurstConfig,
    nrSSBurstStartSymbols,
    nrSSS,
    nrSSSIndices,
    nrWavegenPDCCHConfig,
    nrWavegenPDSCHConfig,
)


def _carrier():
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52
    carrier.SubcarrierSpacing = 30
    return carrier


def test_ssb_only_slot_places_active_beams_and_skips_inactive():
    cfg = nrDLCarrierConfig()
    cfg.Carrier = _carrier()
    cfg.SSBurst = nrSSBurstConfig()
    cfg.SSBurst.BlockPattern = "B"
    cfg.SSBurst.TransmittedBlocks = [1, 0, 1, 0, 0, 0, 0, 0]  # beam0 and beam2 active
    cfg.SSBurst.PRBOffset = 10
    cfg.SSBurst.Period = 20

    grid, info = nrDLCarrierGenerate(cfg, 0)

    # Beam 2's start symbol (16) falls in slot 1, not slot 0 -- only beam 0 should appear.
    assert [b["beamIndex"] for b in info["SSB"]] == [0]

    beam0 = info["SSB"][0]
    assert beam0["PSS"].shape == (127,)
    assert beam0["SSS"].shape == (127,)
    assert beam0["PBCH"].shape == (432,)
    assert beam0["PBCHDMRS"].shape == (144,)
    assert np.count_nonzero(grid) == 127 + 127 + 432 + 144


def test_ssb_content_matches_direct_calls():
    cfg = nrDLCarrierConfig()
    cfg.Carrier = _carrier()
    cfg.Carrier.NFrame = 3
    cfg.SSBurst = nrSSBurstConfig()
    cfg.SSBurst.BlockPattern = "A"
    cfg.SSBurst.TransmittedBlocks = [1, 0, 0, 0]
    cfg.SSBurst.PRBOffset = 0
    cfg.SSBurst.Period = 20
    cfg.SSBurst.NCellID = 42

    grid, info = nrDLCarrierGenerate(cfg, 0)
    beam0 = info["SSB"][0]

    ncellid = 42
    startSymbol = int(nrSSBurstStartSymbols("A", 4)[0])
    sfn, hrf = 3, 0
    v = 2 * ((sfn >> 2) & 1) + ((sfn >> 1) & 1)

    pss = nrPSS(ncellid)
    sss = nrSSS(ncellid)
    coded = nrBCH(np.zeros(24, dtype=int), sfn, hrf, 4, 0, ncellid)
    pbch = nrPBCH(ncellid, v, coded)
    pbchDmrs = nrPBCHDMRS(ncellid, 0)

    totalSC = 12 * cfg.Carrier.NSizeGrid
    pssInd = (nrPSSIndices() % 240) + (startSymbol + nrPSSIndices() // 240) * totalSC
    assert np.array_equal(grid.ravel(order="F")[pssInd], pss)

    sssInd = (nrSSSIndices() % 240) + (startSymbol + nrSSSIndices() // 240) * totalSC
    assert np.array_equal(grid.ravel(order="F")[sssInd], sss)

    pbchGlobalInd = beam0["PBCH"]
    pbchLocalInd = nrPBCHIndices(ncellid)
    order = np.argsort(pbchLocalInd)
    assert np.allclose(grid.ravel(order="F")[np.sort(pbchGlobalInd)], pbch[order])

    dmrsGlobalInd = beam0["PBCHDMRS"]
    dmrsLocalInd = nrPBCHDMRSIndices(ncellid)
    dorder = np.argsort(dmrsLocalInd)
    assert np.allclose(grid.ravel(order="F")[np.sort(dmrsGlobalInd)], pbchDmrs[dorder])


def test_pdsch_avoids_active_ssb_reservation():
    cfg = nrDLCarrierConfig()
    cfg.Carrier = _carrier()
    cfg.SSBurst = nrSSBurstConfig()
    cfg.SSBurst.BlockPattern = "B"
    cfg.SSBurst.TransmittedBlocks = [1, 0, 0, 0, 0, 0, 0, 0]
    cfg.SSBurst.PRBOffset = 10
    cfg.SSBurst.Period = 20

    pdsch = nrWavegenPDSCHConfig()
    pdsch.PDSCH.PRBSet = list(range(52))
    pdsch.PDSCH.SymbolAllocation = [0, 14]
    pdsch.Codeword = np.random.default_rng(0).integers(0, 2, 52 * 12 * 14 * 2)
    cfg.PDSCH = [pdsch]

    grid, info = nrDLCarrierGenerate(cfg, 0)

    totalSC = 12 * cfg.Carrier.NSizeGrid
    ssbSC = set(range(10 * 12, 10 * 12 + 240))
    ssbStartSymbol = int(nrSSBurstStartSymbols("B", 8)[0])
    ssbSymbols = set(range(ssbStartSymbol, ssbStartSymbol + 4))

    pdschInd = info["PDSCH"][0]["indices"]
    sc = pdschInd % totalSC
    sym = pdschInd // totalSC
    collision = np.isin(sc, list(ssbSC)) & np.isin(sym, list(ssbSymbols))
    assert not np.any(collision)


def test_pdsch_avoids_reserved_coreset():
    cfg = nrDLCarrierConfig()
    cfg.Carrier = _carrier()

    coreset = nrCORESETConfig()
    coreset.FrequencyResources = [1] + [0] * 44  # PRBs 0-5
    coreset.Duration = 2
    cfg.CORESET = [coreset]

    pdsch = nrWavegenPDSCHConfig()
    pdsch.PDSCH.PRBSet = list(range(52))
    pdsch.PDSCH.SymbolAllocation = [0, 14]
    pdsch.ReservedCORESET = [0]
    pdsch.Codeword = np.random.default_rng(1).integers(0, 2, 52 * 12 * 14 * 2)
    cfg.PDSCH = [pdsch]

    grid, info = nrDLCarrierGenerate(cfg, 0)

    totalSC = 12 * cfg.Carrier.NSizeGrid
    coresetSC = set(range(0, 72))  # PRBs 0-5 * 12
    pdschInd = info["PDSCH"][0]["indices"]
    sc = pdschInd % totalSC
    sym = pdschInd // totalSC
    collision = np.isin(sc, list(coresetSC)) & np.isin(sym, [0, 1])
    assert not np.any(collision)


def test_pdsch_avoids_reserved_coreset_only_on_slots_it_is_actually_monitored():
    # Regression test: an earlier version never set .Period on the CORESET reservation it built,
    # so it defaulted to None -- meaning (per nrPDSCHReservedConfig's own nslot-projection
    # semantics) the reservation only actually applied at nSlot=0 and silently became a no-op
    # everywhere else, regardless of the referencing search space's own SlotPeriodAndOffset. A
    # CORESET monitored every 4th slot must keep PDSCH off of it on those slots, and free the
    # PRBs back up on the slots in between.
    cfg = nrDLCarrierConfig()
    cfg.Carrier = _carrier()

    coreset = nrCORESETConfig()
    coreset.ControlResourceSetId = 0
    coreset.FrequencyResources = [1] + [0] * 44  # PRBs 0-5
    coreset.Duration = 2
    cfg.CORESET = [coreset]

    pdcch = nrWavegenPDCCHConfig()
    pdcch.PDCCH = nrPDCCHConfig()
    pdcch.PDCCH.CORESET = coreset
    pdcch.PDCCH.SearchSpace = nrSearchSpaceConfig()
    pdcch.PDCCH.SearchSpace.ControlResourceSetId = 0
    pdcch.PDCCH.SearchSpace.SlotPeriodAndOffset = [4, 0]
    pdcch.Bits = np.zeros(108, dtype=int)
    cfg.PDCCH = [pdcch]

    pdsch = nrWavegenPDSCHConfig()
    pdsch.PDSCH.PRBSet = list(range(52))
    pdsch.PDSCH.SymbolAllocation = [0, 14]
    pdsch.ReservedCORESET = [0]
    pdsch.Codeword = np.random.default_rng(1).integers(0, 2, 52 * 12 * 14 * 2)
    cfg.PDSCH = [pdsch]

    totalSC = 12 * cfg.Carrier.NSizeGrid
    coresetSC = set(range(0, 72))  # PRBs 0-5 * 12

    def collides(nSlot):
        _, info = nrDLCarrierGenerate(cfg, nSlot)
        pdschInd = info["PDSCH"][0]["indices"]
        sc = pdschInd % totalSC
        sym = pdschInd // totalSC
        return bool(np.any(np.isin(sc, list(coresetSC)) & np.isin(sym, [0, 1])))

    assert not collides(0)  # monitored (0 % 4 == 0) -> PDSCH must avoid it
    assert not collides(4)  # monitored (4 % 4 == 0) -> PDSCH must avoid it
    assert collides(1)  # not monitored -> PRBs are free for PDSCH
    assert collides(2)  # not monitored -> PRBs are free for PDSCH


def test_reservedprb_does_not_accumulate_across_repeated_calls():
    # Regression test: pdsch.PDSCH.ReservedPRB must be rebuilt fresh every call, not read back
    # and re-appended -- otherwise generating the same config across multiple slots would make
    # the reservation list (and therefore nrPDSCHIndices' cost) grow unboundedly.
    cfg = nrDLCarrierConfig()
    cfg.Carrier = _carrier()

    coreset = nrCORESETConfig()
    coreset.FrequencyResources = [1] + [0] * 44
    coreset.Duration = 1
    cfg.CORESET = [coreset]

    pdsch = nrWavegenPDSCHConfig()
    pdsch.PDSCH.PRBSet = list(range(52))
    pdsch.PDSCH.SymbolAllocation = [0, 14]
    pdsch.ReservedCORESET = [0]
    pdsch.Codeword = np.random.default_rng(2).integers(0, 2, 52 * 12 * 14 * 2)
    cfg.PDSCH = [pdsch]

    for nSlot in range(5):
        nrDLCarrierGenerate(cfg, nSlot)

    assert len(pdsch.PDSCH.ReservedPRB) == 1  # just the one CORESET reservation, not 5x


def test_pdsch_reclaims_ssb_band_when_no_beam_transmits_there():
    # Regression test: an earlier version built a ReservedPRB entry for every one of the Lmax
    # candidate beam positions regardless of TransmittedBlocks, so PDSCH was blocked out of the
    # SSB's PRB range on every slot, even ones where no beam was actually configured to
    # transmit. Only *actually-transmitted* positions (ssb-PositionsInBurst) are off-limits --
    # an untransmitted candidate position is free for the scheduler.
    cfg = nrDLCarrierConfig()
    cfg.Carrier = _carrier()
    cfg.SSBurst = nrSSBurstConfig()
    cfg.SSBurst.BlockPattern = "B"
    cfg.SSBurst.TransmittedBlocks = [1, 0, 0, 0, 0, 0, 0, 0]  # only beam 0 active
    cfg.SSBurst.PRBOffset = 10
    cfg.SSBurst.Period = 20

    pdsch = nrWavegenPDSCHConfig()
    pdsch.PDSCH.PRBSet = list(range(52))
    pdsch.PDSCH.SymbolAllocation = [0, 14]
    pdsch.Codeword = np.random.default_rng(0).integers(0, 2, 52 * 12 * 14 * 2)
    cfg.PDSCH = [pdsch]

    totalSC = 12 * cfg.Carrier.NSizeGrid
    ssbSC = set(range(10 * 12, 10 * 12 + 240))

    # Slot 1: beam 0 (the only active one) doesn't land here -- the SSB's frequency range
    # should be fully usable by PDSCH (240 subcarriers x 13 non-DMRS symbols = 3120 REs).
    _, info = nrDLCarrierGenerate(cfg, 1)
    assert len(info["SSB"]) == 0
    pdschInd = info["PDSCH"][0]["indices"]
    sc = pdschInd % totalSC
    assert np.isin(sc, list(ssbSC)).sum() == 240 * 13


def test_pdcch_symbol_offset_shifts_content_and_matching_pdsch_reservation():
    # Mirrors a second CORESET shifted later in the slot (e.g. symbols 6-8), which real MATLAB
    # models via nrSearchSpaceConfig.StartSymbolWithinSlot -- py3gpp's nrPDCCHResources takes the
    # same offset as an explicit parameter instead (no search-space candidate hashing), and
    # nrDLCarrierGenerate wires it through to both PDCCH's own generation and the matching
    # nrCORESETReservedConfig used to build the PDSCH reservation, so both agree on where the
    # CORESET actually sits.
    cfg = nrDLCarrierConfig()
    cfg.Carrier = _carrier()

    coreset = nrCORESETConfig()
    coreset.ControlResourceSetId = 1
    coreset.FrequencyResources = [1] + [0] * 44  # PRBs 0-5
    coreset.Duration = 3
    cfg.CORESET = [coreset]

    searchSpace = nrSearchSpaceConfig()
    searchSpace.ControlResourceSetId = 1
    searchSpace.StartSymbolWithinSlot = 6

    pdcchConfig = nrPDCCHConfig()
    pdcchConfig.CORESET = coreset
    pdcchConfig.SearchSpace = searchSpace
    pdcchConfig.RNTI = 42

    pdcch = nrWavegenPDCCHConfig()
    pdcch.PDCCH = pdcchConfig
    pdcch.CCEStart = 0
    pdcch.Bits = np.random.default_rng(3).integers(0, 2, 108)  # AL1 -> 1 CCE -> 108 bits
    cfg.PDCCH = [pdcch]

    pdsch = nrWavegenPDSCHConfig()
    pdsch.PDSCH.PRBSet = list(range(52))
    pdsch.PDSCH.SymbolAllocation = [0, 14]
    pdsch.ReservedCORESET = [0]
    pdsch.Codeword = np.random.default_rng(4).integers(0, 2, 52 * 12 * 14 * 2)
    cfg.PDSCH = [pdsch]

    grid, info = nrDLCarrierGenerate(cfg, 0)

    totalSC = 12 * cfg.Carrier.NSizeGrid
    pdcchInd = info["PDCCH"][0]["indices"]
    pdcchSymbols = set((pdcchInd // totalSC).tolist())
    assert pdcchSymbols == {6, 7, 8}  # StartSymbolWithinSlot=6, Duration=3 -> symbols 6,7,8

    pdschInd = info["PDSCH"][0]["indices"]
    coresetSC = set(range(0, 72))  # PRBs 0-5 * 12
    sc = pdschInd % totalSC
    sym = pdschInd // totalSC
    collision = np.isin(sc, list(coresetSC)) & np.isin(sym, [6, 7, 8])
    assert not np.any(collision), "PDSCH reservation must match PDCCH's actual (shifted) symbols"

    # And symbols 0-5 (before the shift) must be free for PDSCH at those same PRBs.
    reclaimed = np.isin(sc, list(coresetSC)) & np.isin(sym, [0, 1, 2, 3, 4, 5])
    assert np.any(reclaimed), "PDSCH should be free to use the CORESET's PRBs before its shifted start symbol"


def test_periodicity_gating():
    cfg = nrDLCarrierConfig()
    cfg.Carrier = _carrier()
    cfg.SSBurst = nrSSBurstConfig()
    cfg.SSBurst.BlockPattern = "A"
    cfg.SSBurst.TransmittedBlocks = [1, 0, 0, 0]
    cfg.SSBurst.Period = 4

    _, info_active = nrDLCarrierGenerate(cfg, 0)
    _, info_inactive = nrDLCarrierGenerate(cfg, 1)

    assert len(info_active["SSB"]) == 1
    assert len(info_inactive["SSB"]) == 0
