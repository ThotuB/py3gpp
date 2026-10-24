import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrCORESETConfig, nrPDCCHResources


def test_nrPDCCHResources_bounds_and_bijective():
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52

    coreset = nrCORESETConfig()
    coreset.FrequencyResources = [1] * 8 + [0] * 37  # 8 groups * 6 RBs = 48 RBs -> 8 CCEs
    coreset.Duration = 2

    cce_indices = [0, 1, 2]
    pdcch_re, dmrs_re = nrPDCCHResources(carrier, coreset, cce_indices)

    total_subcarriers = 12 * carrier.NSizeGrid
    total_symbols = coreset.Duration
    grid_size = total_subcarriers * total_symbols

    # bounds
    assert pdcch_re.min() >= 0
    assert dmrs_re.min() >= 0
    assert pdcch_re.max() < grid_size
    assert dmrs_re.max() < grid_size

    # expected counts: 6 REGs/CCE * 9 data REs/REG, and 6 REGs/CCE * 3 DM-RS REs/REG
    assert pdcch_re.shape == (len(cce_indices) * 6 * 9,)
    assert dmrs_re.shape == (len(cce_indices) * 6 * 3,)

    # bijective over the requested CCEs: no duplicates, and data/DM-RS sets are disjoint
    assert len(np.unique(pdcch_re)) == pdcch_re.size
    assert len(np.unique(dmrs_re)) == dmrs_re.size
    assert not np.any(np.isin(pdcch_re, dmrs_re))


def test_nrPDCCHResources_covers_full_coreset_without_overlap():
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52

    coreset = nrCORESETConfig()
    coreset.FrequencyResources = [1] * 4 + [0] * 41  # 4 groups * 6 RBs = 24 RBs -> 4 CCEs
    coreset.Duration = 1

    all_cces = list(range(4))
    pdcch_re, dmrs_re = nrPDCCHResources(carrier, coreset, all_cces)

    # splitting into disjoint CCE subsets must recombine (as sets) to the same result as doing it all at once
    pdcch_a, dmrs_a = nrPDCCHResources(carrier, coreset, all_cces[:2])
    pdcch_b, dmrs_b = nrPDCCHResources(carrier, coreset, all_cces[2:])

    assert set(pdcch_re.tolist()) == set(pdcch_a.tolist()) | set(pdcch_b.tolist())
    assert set(dmrs_re.tolist()) == set(dmrs_a.tolist()) | set(dmrs_b.tolist())


def test_nrPDCCHResources_out_of_range_cce_asserts():
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52

    coreset = nrCORESETConfig()
    coreset.FrequencyResources = [1] + [0] * 44  # 1 group * 6 RBs = 6 RBs -> 1 CCE
    coreset.Duration = 1

    with pytest.raises(AssertionError):
        nrPDCCHResources(carrier, coreset, [1])  # only CCE 0 exists


def test_nrPDCCHResources_interleaved_not_implemented():
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52

    coreset = nrCORESETConfig()
    coreset.FrequencyResources = [1] * 8 + [0] * 37
    coreset.CCEREGMapping = "interleaved"

    with pytest.raises(NotImplementedError):
        nrPDCCHResources(carrier, coreset, [0])
