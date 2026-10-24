from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .helper import _calc_gold


# v: scrambling sequence phase, 0..7
# n: number of elements in output sequence
def nrPBCHPRBS(ncellid: int, v: int, n: int) -> NDArray[np.int32]:
    seq = _calc_gold(ncellid, n + v * n)
    return seq[v * n :][:n]
