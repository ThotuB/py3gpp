from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from py3gpp.transport_channel_subcomponents.nrCRCEncode import CRCPoly, nrCRCEncode


def _binToInt(bin: NDArray[np.int_]) -> int:
    integer = 0
    for bit in np.flip(bin):
        integer += bit
        integer <<= 1
    return integer


def nrCRCDecode(blkcrc: NDArray[np.int_], poly: CRCPoly, mask: int = 0) -> tuple[NDArray[np.int_], int]:
    encoded = nrCRCEncode(blkcrc, poly, mask)
    L = len(encoded) - len(blkcrc)
    crc = encoded[-L:]
    return encoded[: len(blkcrc) - L], _binToInt(crc)
