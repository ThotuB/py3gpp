from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def nrEqualizeMMSE(
    rxSym: NDArray[np.complexfloating], hest: NDArray[np.complexfloating], nVar: float
) -> tuple[NDArray[np.complexfloating], NDArray[np.floating]]:
    csi = np.abs(hest * np.conj(hest)) + nVar
    # rxEq = rxSym / hest # zero forcing
    rxEq = rxSym * np.conj(hest) / csi
    return rxEq, csi
