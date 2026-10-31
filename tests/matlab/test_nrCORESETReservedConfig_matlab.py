import matlab.engine
import numpy as np
import pytest

from py3gpp import nrCORESETConfig, nrCORESETReservedConfig


def run_nr_coreset_reserved(frequency_resources, duration, start_symbol, coreset_id, n_start_bwp, eng):
    coreset = nrCORESETConfig()
    coreset.ControlResourceSetId = coreset_id
    coreset.FrequencyResources = frequency_resources
    coreset.Duration = duration

    rsv = nrCORESETReservedConfig(coreset, startSymbol=start_symbol)

    matlab_coreset = {
        "CORESETID": float(coreset_id),
        "FrequencyResources": matlab.double([float(v) for v in frequency_resources]),
        "RBOffset": [],
    }
    prb_ref = eng.feval("nr5g.internal.pdcch.getCORESETPRB", matlab_coreset, float(n_start_bwp))
    prb_ref = np.asarray(prb_ref).ravel().astype(int)

    assert np.array_equal(np.sort(rsv.PRBSet), np.sort(prb_ref))
    assert rsv.SymbolSet == list(range(start_symbol, start_symbol + duration))


def test_nr_coreset_reserved_coreset0_matlab(eng):
    freq = [1] + [0] * 44
    run_nr_coreset_reserved(freq, 1, 0, 0, 0, eng)


@pytest.mark.parametrize("duration", [1, 2, 3])
def test_nr_coreset_reserved_duration_sweep_matlab(duration, eng):
    freq = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0] + [0] * 35
    run_nr_coreset_reserved(freq, duration, 0, 0, 0, eng)


def test_nr_coreset_reserved_sparse_frequency_resources_matlab(eng):
    freq = [0] * 45
    freq[0] = 1
    freq[10] = 1
    freq[44] = 1
    run_nr_coreset_reserved(freq, 2, 3, 0, 0, eng)
