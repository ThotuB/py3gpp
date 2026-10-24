# 38.211 7.4.3 SS/PBCH block
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from py3gpp.dl.sig.pbch_dmrs import nrPBCHDMRSIndices
from py3gpp.helper import _calc_gold
from py3gpp.plc.sym import nrSymbolModulate


# v: scrambling sequence phase, 0..7
# n: number of elements in output sequence
def nrPBCHPRBS(ncellid: int, v: int, n: int) -> NDArray[np.int32]:
    seq = _calc_gold(ncellid, n + v * n)
    return seq[v * n :][:n]


def nrPBCH(ncellid: int, v: int, databits: NDArray[np.int_]) -> NDArray[np.complex128]:
    n = len(databits)

    assert ncellid <= 1007 and ncellid >= 0
    assert v >= 0 and v <= 7
    assert n > 0

    # Scrambling, Section 7.3.3.1, TS 38.211
    prbs_bits = nrPBCHPRBS(ncellid, v, n)
    scrambled_bits = np.bitwise_xor(databits, prbs_bits)

    # Modulation, Section 7.3.3.2, TS 38.211
    res_sym = nrSymbolModulate(scrambled_bits, "QPSK")

    return np.array(res_sym)


def nrPBCHIndices(ibar: int) -> NDArray[np.int_]:
    indices = np.hstack((np.arange(240, 480), np.arange(480, 528), np.arange(672, 720), np.arange(720, 960)))
    return np.setdiff1d(indices, nrPBCHDMRSIndices(ibar))
