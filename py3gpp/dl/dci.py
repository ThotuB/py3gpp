# Ref: TS 38.212 Section 7.3.2
from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from py3gpp.plc.trs.crc import nrCRCDecode, nrCRCEncode
from py3gpp.plc.trs.polar import nrPolarDecode, nrPolarEncode, nrRateMatchPolar, nrRateRecoverPolar


def nrDCIEncode(dcibits: NDArray[np.int_], rnti: int, E: int, nmax: Literal[9, 10] = 9) -> NDArray[np.int_]:
    """Encode downlink control information (DCI)."""
    crcbits = nrCRCEncode(dcibits, "24C", mask=rnti)[:, 0]
    encoded = nrPolarEncode(crcbits, E, nmax=nmax, iil=True)
    return nrRateMatchPolar(encoded, 0, E)


def nrDCIDecode(
    softbits: NDArray[np.float64], dcilen: int, rnti: int, nmax: Literal[9, 10] = 9, L: int = 8
) -> tuple[NDArray[np.int_], int]:
    """Decode downlink control information (DCI)."""
    K = dcilen + 24
    N = 2**nmax
    matched = nrRateRecoverPolar(softbits, K, N, False, False)
    decoded = nrPolarDecode(matched, K, len(softbits), L, nmax=nmax)
    dcibits, crc_result = nrCRCDecode(decoded, "24C", mask=rnti)
    return dcibits[:, 0], crc_result
