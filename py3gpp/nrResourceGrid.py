from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from py3gpp.configs.nrCarrierConfig import nrCarrierConfig


def nrResourceGrid(carrier: nrCarrierConfig, p: int = 1) -> NDArray[np.complex128]:
    SymbolsPerSlot = 14
    if p == 1:
        grid = np.zeros((12 * carrier.NSizeGrid, SymbolsPerSlot), "complex")
    else:
        grid = np.zeros((12 * carrier.NSizeGrid, SymbolsPerSlot, p), "complex")
    return grid
