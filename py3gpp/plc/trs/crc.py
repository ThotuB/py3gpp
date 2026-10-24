from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

CRCPoly = Literal["6", "11", "16", "24A", "24B", "24C"]


def nrCRCEncode(blk: NDArray[np.int_], poly: CRCPoly, mask: int = 0) -> NDArray[np.int_]:
    """CRC encoding."""
    if len(blk.shape) == 1:
        blk = np.expand_dims(blk, axis=1)
    if poly == "6":
        L = 6
        # fmt: off
        crc_coeffs = [6, 5, 0]
        # fmt: on
    elif poly == "11":
        L = 11
        # fmt: off
        crc_coeffs = [11, 10, 9, 5, 0]
        # fmt: on
    elif poly == "16":
        L = 16
        # fmt: off
        crc_coeffs = [16, 12, 5, 0]
        # fmt: on
    elif poly == "24A":
        L = 24
        # fmt: off
        crc_coeffs = [24, 23, 18, 17, 14, 11, 10, 7, 6, 5, 4, 3, 1, 0]
        # fmt: on
    elif poly == "24B":
        L = 24
        # fmt: off
        crc_coeffs = [24, 23, 6, 5, 1, 0]
        # fmt: on
    elif poly == "24C":
        L = 24
        # fmt: off
        crc_coeffs = [24, 23, 21, 20, 17, 15, 13, 12, 8, 4, 2, 1, 0]
        # fmt: on
    else:
        raise ValueError("invalid CRC polynomial specified!")
    blksrc = np.empty((len(blk) + L, 1), "int")
    blksrc[: len(blk)] = blk

    # build crc_poly
    crc_poly = 0
    for crc_coeff in crc_coeffs:
        crc_poly += 2**crc_coeff

    # calculate crc
    crc = 0
    for bit in blk:
        if ((crc >> (L - 1)) & 1) != bit:
            crc = (crc << 1) ^ crc_poly
        else:
            crc = crc << 1
    crc ^= mask

    # append crc LSB first
    for i in range(L):
        blksrc[len(blk) + i] = (crc >> (L - i - 1)) & 1
    return blksrc


def _binToInt(bin: NDArray[np.int_]) -> int:
    integer = 0
    for bit in np.flip(bin):
        integer += bit
        integer <<= 1
    return integer


def nrCRCDecode(blkcrc: NDArray[np.int_], poly: CRCPoly, mask: int = 0) -> tuple[NDArray[np.int_], int]:
    """CRC decoding."""
    blkcrc = np.asarray(blkcrc).ravel()
    probe = nrCRCEncode(blkcrc, poly, 0)
    L = len(probe) - len(blkcrc)
    if mask:
        # The standard "recompute CRC over payload+embedded-crc, check for zero" trick only
        # works when mask == 0: nrCRCEncode's masking XORs mask into its own freshly computed
        # remainder *after* an extra x^L shift, which does not invert cleanly when re-encoding
        # the full (payload + masked crc) blob. Unmask the embedded CRC bits back to their raw
        # (unmasked) form first, so the usual zero-check applies correctly for any mask.
        received_crc_int = 0
        for bit in blkcrc[-L:]:
            received_crc_int = (received_crc_int << 1) | int(bit)
        raw_crc_int = received_crc_int ^ mask
        raw_crc_bits = [(raw_crc_int >> (L - i - 1)) & 1 for i in range(L)]
        blkcrc = np.concatenate([blkcrc[:-L], np.array(raw_crc_bits, int)])
    encoded = nrCRCEncode(blkcrc, poly, 0)
    crc = encoded[-L:]
    return encoded[: len(blkcrc) - L], _binToInt(crc)
