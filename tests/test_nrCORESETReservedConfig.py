import numpy as np

from py3gpp import nrCarrierConfig, nrCORESETConfig, nrCORESETReservedConfig, nrPDSCHConfig, nrPDSCHIndices


def test_prbset_matches_frequency_resources_bitmap():
    coreset = nrCORESETConfig()
    coreset.FrequencyResources = [1, 0, 1] + [0] * 42
    coreset.Duration = 2

    rsv = nrCORESETReservedConfig(coreset)

    assert rsv.PRBSet == list(range(0, 6)) + list(range(12, 18))


def test_symbolset_matches_duration_and_start_symbol():
    coreset = nrCORESETConfig()
    coreset.Duration = 3

    rsv = nrCORESETReservedConfig(coreset, startSymbol=0)
    assert rsv.SymbolSet == [0, 1, 2]

    rsv2 = nrCORESETReservedConfig(coreset, startSymbol=4)
    assert rsv2.SymbolSet == [4, 5, 6]


def test_period_left_unset_by_default():
    coreset = nrCORESETConfig()
    rsv = nrCORESETReservedConfig(coreset)
    assert rsv.Period is None


def test_wired_into_pdsch_excludes_coreset_region():
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = 30
    carrier.NSizeGrid = 52
    carrier.NSlot = 0

    coreset = nrCORESETConfig()
    coreset.FrequencyResources = [1] + [0] * 44
    coreset.Duration = 2

    pdsch = nrPDSCHConfig()
    pdsch.PRBSet = list(range(52))
    pdsch.SymbolAllocation = [0, 14]

    plain = nrPDSCHIndices(carrier, pdsch)

    pdsch.ReservedPRB = [nrCORESETReservedConfig(coreset, startSymbol=0)]
    reserved = nrPDSCHIndices(carrier, pdsch)

    assert reserved.shape[0] < plain.shape[0]

    totalSC = carrier.NSizeGrid * pdsch.NRBSize
    coreset_sc = np.arange(0, 6 * pdsch.NRBSize)
    for sym in range(2):
        assert not np.any(np.isin(reserved, coreset_sc + sym * totalSC))
