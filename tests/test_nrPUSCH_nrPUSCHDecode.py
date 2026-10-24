import numpy as np
import pytest

from py3gpp import nrPUSCH, nrPUSCHDecode

MOD_PAIRS = [
    ("bpsk", "BPSK"),
    ("qpsk", "QPSK"),
    ("16qam", "16QAM"),
    ("64qam", "64QAM"),
    ("256qam", "256QAM"),
]


@pytest.mark.parametrize("mod_enc,mod_dec", MOD_PAIRS)
def test_nrPUSCH_nrPUSCHDecode_round_trip_no_precoding(mod_enc, mod_dec):
    rng = np.random.default_rng(0)
    bits_per_sym = {"bpsk": 1, "qpsk": 2, "16qam": 4, "64qam": 6, "256qam": 8}[mod_enc]
    cw = rng.integers(0, 2, bits_per_sym * 300)
    rnti, nid = 123, 5

    syms = nrPUSCH(cw, mod_enc, 1, nid, rnti)
    assert syms.shape == (1, len(cw) // bits_per_sym)
    assert syms.dtype == np.complex128

    recovered = nrPUSCHDecode(syms, mod_dec, nid, rnti)
    recovered_bits = (recovered[0] < 0).astype(int)
    assert np.array_equal(recovered_bits, cw)


@pytest.mark.parametrize("mrb", [1, 4, 25])
def test_nrPUSCH_nrPUSCHDecode_round_trip_transform_precoding(mrb):
    rng = np.random.default_rng(1)
    num_syms = mrb * 12 * 3  # 3 "OFDM symbols" worth of QPSK data
    cw = rng.integers(0, 2, 2 * num_syms)
    rnti, nid = 42, 7

    syms = nrPUSCH(cw, "qpsk", 1, nid, rnti, mrb=mrb, transform_precoding="enabled")
    assert syms.shape == (1, num_syms)

    recovered = nrPUSCHDecode(syms, "QPSK", nid, rnti, mrb=mrb, transform_precoding="enabled")
    recovered_bits = (recovered[0] < 0).astype(int)
    assert np.array_equal(recovered_bits, cw)


def test_nrPUSCH_transform_precoding_requires_mrb():
    rng = np.random.default_rng(2)
    cw = rng.integers(0, 2, 48)
    with pytest.raises(AssertionError):
        nrPUSCH(cw, "qpsk", 1, 0, 0, transform_precoding="enabled")


def test_nrPUSCH_multilayer_not_implemented():
    rng = np.random.default_rng(3)
    cw = rng.integers(0, 2, 48)
    with pytest.raises(NotImplementedError):
        nrPUSCH(cw, "qpsk", 2, 0, 0)
