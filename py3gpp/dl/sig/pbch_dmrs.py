from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from py3gpp.plc.sym import nrPRBS, nrSymbolModulate


def nrPBCHDMRS(ncellid: int, ibar_SSB: int) -> NDArray[np.complex128]:
    assert ncellid >= 0 and ncellid <= 1007
    assert ibar_SSB >= 0 and ibar_SSB <= 7

    c_init = nrPBCHDMRScinit(ibar_SSB, ncellid)
    c = nrPRBS(c_init, 2 * 144)

    return nrSymbolModulate(c, "qpsk")


def nrPBCHDMRScinit(issb: int, ncellid: int) -> int:
    return 2**11 * (issb + 1) * (ncellid // 4 + 1) + 2**6 * (issb + 1) + (ncellid % 4)


def nrPBCHDMRSIndices(
    ncellid: int, style: Literal["python", "matlab"] = "matlab"
) -> tuple[tuple[int, ...], tuple[int, ...]] | NDArray[np.int_]:
    indices_sym1_3 = np.arange(ncellid % 4, 240, 4)
    indices_sym2 = np.concatenate((np.arange(ncellid % 4, 48, 4), np.arange(192 + ncellid % 4, 240, 4)))
    if style == "python":
        indices = np.concatenate((indices_sym1_3, indices_sym2, indices_sym1_3))
        symbol_idx = np.concatenate(
            (1 * np.ones(len(indices_sym1_3)), 2 * np.ones(len(indices_sym2)), 3 * np.ones(len(indices_sym1_3)))
        ).astype("int")
        return (tuple(indices), tuple(symbol_idx))
    elif style == "matlab":
        indices = np.concatenate((indices_sym1_3 + 240, indices_sym2 + 2 * 240, indices_sym1_3 + 3 * 240))
        return indices
    else:
        raise ValueError("Unknown style!")
    return
