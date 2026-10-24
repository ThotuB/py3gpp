from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from py3gpp.downlink_physical_signals.nrPBCHDMRSIndices import nrPBCHDMRSIndices


def nrPBCHIndices(ibar: int) -> NDArray[np.int_]:
    indices = np.hstack((np.arange(240, 480), np.arange(480, 528), np.arange(672, 720), np.arange(720, 960)))
    return np.setdiff1d(indices, nrPBCHDMRSIndices(ibar))
