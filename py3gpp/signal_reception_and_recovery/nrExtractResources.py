from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray


def nrExtractResources(ind: NDArray[np.int_], grid: NDArray[Any]) -> NDArray[Any]:
    return grid.ravel(order="F")[ind]
