import itertools

import matlab.engine
from matlab.engine.matlabengine import MatlabEngine
import numpy as np
import pytest

from py3gpp.ul.ch.trs.uci import nrUCIDecode, nrUCIEncode


def run_nr_uci_encode(uci_bits, euci, modulation, eng):
    encoded = nrUCIEncode(uci_bits, euci, modulation)

    ref = eng.nrUCIEncode(matlab.double(uci_bits.tolist()), matlab.double(euci), modulation)
    ref = np.array(list(itertools.chain(*ref))).astype(int)

    assert encoded.shape == ref.shape
    assert np.array_equal(encoded, ref)
    return encoded


def run_nr_uci_decode(encoded, a, modulation, eng):
    soft_bits = 1.0 - 2.0 * encoded.astype(float)

    bits, err = nrUCIDecode(soft_bits, a, modulation)

    ref_bits, ref_err = eng.nrUCIDecode(matlab.double(soft_bits.tolist()), matlab.double(a), modulation, nargout=2)
    ref_bits = np.array(list(itertools.chain(*ref_bits))).astype(int)

    assert not err
    assert not ref_err
    assert np.array_equal(bits, ref_bits)


@pytest.fixture(scope="session")
def eng():
    eng = matlab.engine.connect_matlab()
    assert isinstance(eng, MatlabEngine)
    yield eng
    eng.quit()


@pytest.mark.parametrize("a", [1, 2])
@pytest.mark.parametrize("modulation", ["QPSK", "16QAM"])
def test_nr_uci_small_a1_2_matlab(a, modulation, eng):
    rng = np.random.default_rng(a * 100 + hash(modulation) % 7)
    uci_bits = rng.integers(0, 2, a)
    euci = 48
    encoded = run_nr_uci_encode(uci_bits, euci, modulation, eng)
    run_nr_uci_decode(encoded, a, modulation, eng)


@pytest.mark.parametrize("a", [3, 6, 11])
def test_nr_uci_reed_muller_matlab(a, eng):
    rng = np.random.default_rng(a)
    uci_bits = rng.integers(0, 2, a)
    euci = 64
    encoded = run_nr_uci_encode(uci_bits, euci, "QPSK", eng)
    run_nr_uci_decode(encoded, a, "QPSK", eng)


@pytest.mark.parametrize("a", [20, 100, 359])
def test_nr_uci_polar_matlab(a, eng):
    rng = np.random.default_rng(a)
    uci_bits = rng.integers(0, 2, a)
    euci = 864
    encoded = run_nr_uci_encode(uci_bits, euci, "QPSK", eng)
    run_nr_uci_decode(encoded, a, "QPSK", eng)
