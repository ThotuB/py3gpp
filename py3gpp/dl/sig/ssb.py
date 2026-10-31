# Ref: TS 38.213 Section 4.1, Table 4.1-1
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

# Case -> (m, i, nl): the first symbols of the candidate SS/PBCH blocks are i + m*n, where i, m
# are case-dependent constants and n ranges over a case-dependent set (see below). nl is the
# number of n values to take for L_max=4 (cases A-C double this for L_max=8; cases D-G always
# use L_max=64, per TS 38.213 Section 4.1 and the carrier config that feeds this function).
_M = {"A": 14, "B": 28, "C": 14, "D": 28, "E": 56, "F": 14, "G": 14}
_I = {
    "A": [2, 8],
    "B": [4, 8, 16, 20],
    "C": [2, 8],
    "D": [4, 8, 16, 20],
    "E": [8, 12, 16, 20, 32, 36, 40, 44],
    "F": [2, 9],
    "G": [2, 9],
}
_NL = {"A": 2, "B": 1, "C": 2, "D": 16, "E": 8, "F": 32, "G": 32}

# TS 38.213 Section 4.1: the overall set of candidate SS/PBCH block indices n for Cases A-E;
# Cases F-G (FR2-2 / shared spectrum) use the full 0..31 range instead.
_N_ABCDE = np.array([0, 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18])


def nrSSBurstStartSymbols(caseName: str, lMax: int) -> NDArray[np.int_]:
    """Candidate SS/PBCH block first-symbol offsets within a half-frame (TS 38.213 Table 4.1-1)."""
    case = caseName.removeprefix("Case ").removeprefix("case ").upper()
    assert case in _M, "caseName must be one of 'A'..'G' (optionally prefixed with 'Case ')"

    nl = _NL[case]
    if case in ("A", "B", "C"):
        assert lMax in (4, 8), "lMax must be 4 or 8 for Case A/B/C"
        if lMax == 8:
            nl *= 2
    else:
        assert lMax == 64, "lMax must be 64 for Case D/E/F/G"

    n = _N_ABCDE if case in ("A", "B", "C", "D", "E") else np.arange(32)
    n = n[:nl]

    i = np.array(_I[case])
    m = _M[case]
    return (i[:, None] + m * n[None, :]).ravel(order="F")
