# Ref: TS 38.211 Section 7.3.2
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from py3gpp.plc.sym import nrPRBS, nrSymbolDemodulate, nrSymbolModulate


def nrPDCCHPRBS(rnti: int, nid: int, length: int) -> NDArray[np.int32]:
    """Generate PDCCH scrambling sequence."""
    cinit = (rnti * 2**16 + nid) % 2**31
    return nrPRBS(cinit, length)


def nrPDCCH(bits: NDArray[np.int_], rnti: int, nid: int) -> NDArray[np.complex128]:
    """Generate PDCCH modulation symbols."""
    scrambling_seq = nrPDCCHPRBS(rnti, nid, len(bits))
    scrambled = np.bitwise_xor(bits, scrambling_seq)
    return nrSymbolModulate(scrambled, "QPSK")


def nrPDCCHDecode(sym: NDArray[np.complex128], rnti: int, nid: int) -> NDArray[np.float64]:
    """Decode PDCCH modulation symbols."""
    demod = nrSymbolDemodulate(sym, "QPSK")
    scrambling_seq = nrPDCCHPRBS(rnti, nid, len(demod))
    return np.multiply(demod, (-scrambling_seq * 2 + 1))
