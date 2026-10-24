from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from py3gpp.nrPRBS import nrPRBS
from py3gpp.nrSymbolModulate import nrSymbolModulate


def nrPBCHDMRS(ncellid: int, ibar_SSB: int) -> NDArray[np.complex128]:
    assert ncellid >= 0 and ncellid <= 1007
    assert ibar_SSB >= 0 and ibar_SSB <= 7

    c_init = nrPBCHDMRScinit(ibar_SSB, ncellid)
    c = nrPRBS(c_init, 2 * 144)

    return nrSymbolModulate(c, "qpsk")


def nrPBCHDMRScinit(issb: int, ncellid: int) -> int:
    return 2**11 * (issb + 1) * (ncellid // 4 + 1) + 2**6 * (issb + 1) + (ncellid % 4)
