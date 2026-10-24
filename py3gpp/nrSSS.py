from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from py3gpp.helper import _calc_m_seq


def nrSSSm0(ncellid: int) -> int:
    n1 = ncellid // 3
    n2 = ncellid % 3
    return 15 * (n1 // 112) + 5 * n2


def nrSSSm1(ncellid: int) -> int:
    n1 = ncellid // 3
    return n1 % 112


def _gold(ncellid: int) -> NDArray[np.int_]:
    N = 7
    c = [1, 0, 0, 0, 0, 0, 0]
    taps_0 = [0, 4]
    taps_1 = [0, 1]
    mseq_0 = _calc_m_seq(N, c, taps_0)
    mseq_1 = _calc_m_seq(N, c, taps_1)
    m_0 = nrSSSm0(ncellid)
    m_1 = nrSSSm1(ncellid)
    d_SSS = (1 - 2 * np.roll(mseq_0, -m_0)) * (1 - 2 * np.roll(mseq_1, -m_1))
    return d_SSS


def nrSSS(ncellid: int) -> NDArray[np.int_]:
    assert ncellid >= 0 and ncellid <= 1007, "invalid ncellid"
    return _gold(ncellid)
