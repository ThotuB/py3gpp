import numpy as np

from py3gpp import nrCarrierConfig, nrPRSConfig, nrPRSIndices


def test_nrPRSIndices_default_matches_matlab():
    # Reference indices captured from a live MATLAB 5G Toolbox (R2026a) session, converted
    # from MATLAB's 1-based indexing.
    carrier = nrCarrierConfig()
    prs = nrPRSConfig()
    ind = nrPRSIndices(carrier, prs)

    assert ind.shape == (3744,)
    assert ind[0] == 0
    assert ind[-1] == 7487
    assert len(np.unique(ind)) == ind.size


def test_nrPRSIndices_multi_resource_muting_matches_matlab():
    carrier = nrCarrierConfig()
    carrier.NSlot = 0
    prs = nrPRSConfig()
    prs.PRSResourceSetPeriod = [8, 0]
    prs.PRSResourceOffset = [0, 4]
    prs.PRSResourceRepetition = 2
    prs.PRSResourceTimeGap = 1
    prs.MutingPattern1 = [1, 1]
    prs.MutingBitRepetition = 1
    prs.MutingPattern2 = [1, 0]
    prs.NumPRSSymbols = [6, 12]
    prs.SymbolStart = [6, 0]
    prs.NumRB = 40
    prs.RBOffset = 4
    prs.CombSize = 4
    prs.REOffset = [1, 3]
    prs.NPRSID = 5

    ind = nrPRSIndices(carrier, prs)
    assert ind.shape == (720,)
    assert ind[0] == 3793
    assert ind[-1] == 7391
    assert len(np.unique(ind)) == ind.size


def test_nrPRSIndices_nonzero_nstartgrid():
    carrier = nrCarrierConfig()
    carrier.NStartGrid = 10
    carrier.NSizeGrid = 106
    carrier.NSlot = 7
    prs = nrPRSConfig()
    prs.CombSize = 6
    prs.NumRB = 30
    prs.RBOffset = 5
    prs.NPRSID = 200
    prs.REOffset = 3

    ind = nrPRSIndices(carrier, prs)
    assert ind.shape == (720,)
    assert ind.min() >= 0
    assert ind.max() < carrier.NSizeGrid * 12 * carrier.SymbolsPerSlot
    assert len(np.unique(ind)) == ind.size


def test_nrPRSIndices_resource_set_off_is_empty():
    carrier = nrCarrierConfig()
    prs = nrPRSConfig()
    prs.PRSResourceSetPeriod = "off"
    ind = nrPRSIndices(carrier, prs)
    assert ind.shape == (0,)
