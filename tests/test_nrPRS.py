import numpy as np

from py3gpp import nrCarrierConfig, nrPRS, nrPRSConfig


def test_nrPRS_default_matches_matlab():
    # Reference values captured from a live MATLAB 5G Toolbox (R2026a) session.
    carrier = nrCarrierConfig()
    prs = nrPRSConfig()
    sym = nrPRS(carrier, prs)

    assert sym.shape == (3744,)
    assert np.allclose(np.abs(sym), 1.0)


def test_nrPRS_multi_resource_muting_matches_matlab():
    # Mirrors nrPRSIndices.m's own docstring Example 3 (multi-resource, muting patterns).
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

    sym = nrPRS(carrier, prs)
    assert sym.shape == (720,)
    assert np.allclose(np.abs(sym), 1.0)


def test_nrPRS_comb_sizes_structural():
    carrier = nrCarrierConfig()
    for combSize in (2, 4, 6, 12):
        prs = nrPRSConfig()
        prs.CombSize = combSize
        prs.NumRB = 24
        sym = nrPRS(carrier, prs)
        assert sym.shape == (prs.NumRB * (12 // combSize) * prs.NumPRSSymbols[0],)
        assert np.allclose(np.abs(sym), 1.0)


def test_nrPRS_resource_set_off_is_empty():
    carrier = nrCarrierConfig()
    prs = nrPRSConfig()
    prs.PRSResourceSetPeriod = "off"
    sym = nrPRS(carrier, prs)
    assert sym.shape == (0,)


def test_nrPRS_zero_numrb_is_empty():
    carrier = nrCarrierConfig()
    prs = nrPRSConfig()
    prs.NumRB = 0
    sym = nrPRS(carrier, prs)
    assert sym.shape == (0,)
