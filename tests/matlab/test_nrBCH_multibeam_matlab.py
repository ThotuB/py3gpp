import itertools
import os

import matlab.engine
import numpy as np
import pytest

from py3gpp.dl.ch.trs.bch import nrBCH, nrBCHDecode


def run_nr_bch(trblk, sfn, hrf, lssb, idxoffset, ncellid, eng):
    cdblk = nrBCH(trblk, sfn, hrf, lssb, idxoffset, ncellid)

    ref = eng.nrBCH(
        matlab.double([[v] for v in trblk.tolist()]),
        float(sfn),
        float(hrf),
        float(lssb),
        float(idxoffset),
        float(ncellid),
    )
    ref = np.array(list(itertools.chain(*ref))).astype(int)

    assert cdblk.shape == ref.shape
    assert np.array_equal(cdblk, ref)
    return cdblk


def run_nr_bch_decode(cdblk, lssb, idxoffset, ncellid, eng):
    soft_bits = 1.0 - 2.0 * cdblk.astype(float)

    result = nrBCHDecode(soft_bits, 8, lssb, ncellid)
    assert len(result) == 6
    scrblk, crc_result, payload, lsbotfsfn, hrf_out, msbidxoffset = result

    ref = eng.nrBCHDecode(
        matlab.double([[v] for v in soft_bits.tolist()]),
        8.0,
        float(lssb),
        float(ncellid),
        nargout=6,
    )
    _, ref_err, ref_payload, ref_lsb, ref_hrf, ref_msbidxoffset = ref

    assert not crc_result
    assert not ref_err
    ref_payload = np.array(list(itertools.chain(*ref_payload))).astype(int)
    assert np.array_equal(payload, ref_payload)
    ref_lsb = np.array(list(itertools.chain(*ref_lsb))).astype(int)
    assert np.array_equal(lsbotfsfn, ref_lsb)
    assert hrf_out == int(ref_hrf)

    # For Lssb=64, MATLAB's MSBIDXOFFSET is the 3 raw MSB bits (a 3-element matlab.logical
    # vector) -- combine them the same way py3gpp's nrBCHDecode does (4*bit0 + 2*bit1 + bit2)
    # before comparing to its single combined integer. For Lssb=4/8 it's already a scalar.
    if hasattr(ref_msbidxoffset, "__len__") and len(ref_msbidxoffset) == 3:
        bits = [int(bool(v[0])) for v in ref_msbidxoffset]
        ref_msbidxoffset_combined = 4 * bits[0] + 2 * bits[1] + bits[2]
    else:
        ref_msbidxoffset_combined = int(ref_msbidxoffset)
    assert msbidxoffset == ref_msbidxoffset_combined


def _fixed_trblk():
    # Same trblk as the existing hand-verified test_nrBCH_multibeam_matches_matlab, so a failure
    # here isolates idxoffset/lssb as the cause, not some other (trblk-content-dependent) factor.
    return np.array([0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0])


@pytest.mark.parametrize("ssb_index", [0, 1, 37, 62, 63])
def test_nr_bch_lssb64_multibeam_matlab(ssb_index, eng):
    eng.cd(os.path.dirname(__file__))
    trblk = _fixed_trblk()
    sfn, hrf, ncellid = 10, 1, 321

    cdblk = run_nr_bch(trblk, sfn, hrf, 64, ssb_index, ncellid, eng)
    run_nr_bch_decode(cdblk, 64, ssb_index, ncellid, eng)


@pytest.mark.parametrize("lssb", [4, 8])
@pytest.mark.parametrize("kssb", [0, 1, 18, 30, 31])
def test_nr_bch_lssb4_8_kssb_matlab(lssb, kssb, eng):
    eng.cd(os.path.dirname(__file__))
    trblk = _fixed_trblk()
    sfn, hrf, ncellid = 10, 1, 321

    cdblk = run_nr_bch(trblk, sfn, hrf, lssb, kssb, ncellid, eng)
    run_nr_bch_decode(cdblk, lssb, kssb, ncellid, eng)
