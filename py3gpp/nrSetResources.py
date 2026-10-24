from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray


# this function does not exist in Matlab, but its useful in python because
# numpy does not support integer indexing across dimensions
def nrSetResources(ind: NDArray[np.int_], grid: NDArray[Any], vals: NDArray[Any]) -> NDArray[Any]:
    nSymbols = grid.shape[0]
    for i in range(grid.shape[1]):
        idx = np.where(np.logical_and(ind >= i * nSymbols, ind < (i + 1) * nSymbols))[0]
        if len(idx) != 0:
            grid[ind[idx] - i * nSymbols, i] = vals[idx]
    return vals
