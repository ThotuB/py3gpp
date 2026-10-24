from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from py3gpp.dl.ch.phy.pbch import nrPBCHPRBS
from py3gpp.plc.trs.crc import nrCRCDecode, nrCRCEncode
from py3gpp.plc.trs.polar import nrPolarDecode, nrPolarEncode, nrRateMatchPolar, nrRateRecoverPolar


def nrBCH(trblk: NDArray[np.int_], sfn: int, hrf: int, lssb: int, idxoffset: int, ncellid: int) -> NDArray[np.int_]:
    """Broadcast channel (BCH) encoding."""
    # interleaving according to TS38.212 7.1.1
    # fmt: off
    G = [16, 23, 18, 17, 8, 30, 10, 6, 24, 7, 0, 5, 3, 2, 1, 4, 9, 11, 12, 13, 14, 15, 19, 20, 21, 22, 25, 26, 27, 28,
         29, 31]
    # fmt: on
    SFN_PAYLOAD_BEGIN = 1
    SFN_PAYLOAD_LENGTH = 6
    SFN_2ND_LSB = SFN_PAYLOAD_LENGTH + 2
    SFN_3RD_LSB = SFN_PAYLOAD_LENGTH + 1
    # v = 2 * scrblk[G[SFN_3RD_LSB]] + scrblk[G[SFN_2ND_LSB]]
    j_sfn = 0
    j_other = 14
    payload = trblk
    A = 32
    a = np.zeros(A, "int")
    for i in range(24):
        if (i >= SFN_PAYLOAD_BEGIN) and (i < (SFN_PAYLOAD_BEGIN + SFN_PAYLOAD_LENGTH)):
            a[G[j_sfn]] = payload[i]
            j_sfn += 1
        else:
            a[G[j_other]] = payload[i]
            j_other += 1
    a[G[10]] = hrf
    a[G[j_sfn + 0]] = 1 if sfn & 0x08 != 0 else 0
    a[G[j_sfn + 1]] = 1 if sfn & 0x04 != 0 else 0
    a[G[j_sfn + 2]] = 1 if sfn & 0x02 != 0 else 0
    a[G[j_sfn + 3]] = 1 if sfn & 0x01 != 0 else 0

    # scramble
    tmp_seq = nrPBCHPRBS(ncellid, 0, len(a) * 100)
    if lssb in (4, 8):
        M = A - 3
    else:
        M = A - 6
    v = 2 * a[G[SFN_3RD_LSB]] + a[G[SFN_2ND_LSB]]
    n = v * M
    scrambling_seq = tmp_seq[n:][:A]
    scrambling_seq_final = np.zeros(A, "int")
    j = 0
    for i in range(A):
        is_ssb_idx = (i in (G[11], G[12], G[13])) and lssb == 64
        if is_ssb_idx or i == G[10] or i == G[SFN_2ND_LSB] or i == G[SFN_3RD_LSB]:
            scrambling_seq_final[i] = 0
        else:
            scrambling_seq_final[i] = scrambling_seq[j]
            j += 1
    scrblk_scrambled = np.bitwise_xor(scrambling_seq_final, a)

    # attach CRC
    bits = nrCRCEncode(scrblk_scrambled, "24C")[:, 0]

    # polar encoding + rate matching
    E = 864
    NMAX = 9
    encoded = nrPolarEncode(bits, 0, nmax=NMAX, iil=True)
    rate_matched = nrRateMatchPolar(encoded, 0, E, ibil=False)

    return rate_matched


def nrBCHDecode(
    softbits: NDArray[np.float64], L: int, lssb: int | None = None, ncellid: int | None = None
) -> tuple[NDArray[np.int_], int] | tuple[NDArray[np.int_], int, NDArray[np.int_], NDArray[np.int_], int, int]:
    """Broadcast channel (BCH) decoding."""
    K = 32 + 24
    E = 864
    L = 8
    N = 512
    matched = nrRateRecoverPolar(softbits, K, N, False, False)

    decoded = nrPolarDecode(matched, K, E, L)
    scrblk, crc_result = nrCRCDecode(decoded, "24C")
    scrblk = scrblk[:, 0]

    if (lssb is None) or (ncellid is None):
        return scrblk, crc_result

    # descrambling according to TS38.212 7.1.2
    # fmt: off
    G = [16, 23, 18, 17, 8, 30, 10, 6, 24, 7, 0, 5, 3, 2, 1, 4, 9, 11, 12, 13, 14, 15, 19, 20, 21, 22, 25, 26, 27, 28,
         29, 31]
    # fmt: on
    SFN_PAYLOAD_BEGIN = 1
    SFN_PAYLOAD_LENGTH = 6
    SFN_2ND_LSB = SFN_PAYLOAD_LENGTH + 2
    SFN_3RD_LSB = SFN_PAYLOAD_LENGTH + 1
    v = 2 * scrblk[G[SFN_3RD_LSB]] + scrblk[G[SFN_2ND_LSB]]

    L_max = 8  # TODO: fix this
    A = 32
    if L_max in (4, 8):
        M = A - 3
    else:
        M = A - 6
    n = v * M
    tmp_seq = nrPBCHPRBS(ncellid, 0, len(scrblk) * 100)
    scrambling_seq = tmp_seq[n:][:A]
    scrambling_seq_final = np.zeros(A, "int")
    j = 0
    for i in range(A):
        is_ssb_idx = (i in (G[11], G[12], G[13])) and L_max == 64
        if is_ssb_idx or i == G[10] or i == G[SFN_2ND_LSB] or i == G[SFN_3RD_LSB]:
            scrambling_seq_final[i] = 0
        else:
            scrambling_seq_final[i] = scrambling_seq[j]
            j += 1
    a = np.bitwise_xor(scrambling_seq_final, scrblk)

    # deinterleaving according to TS38.212 7.1.1
    j_sfn = 0
    j_other = 14
    payload = np.empty(24, "int")
    for i in range(24):
        if (i >= SFN_PAYLOAD_BEGIN) and (i < (SFN_PAYLOAD_BEGIN + SFN_PAYLOAD_LENGTH)):
            payload[i] = a[G[j_sfn]]
            j_sfn += 1
        else:
            payload[i] = a[G[j_other]]
            j_other += 1
    lsbotfsfn = np.array([a[G[j_sfn]], a[G[j_sfn + 1]], a[G[j_sfn + 2]], a[G[j_sfn + 3]]])
    hrf = a[G[10]]
    msbidxoffset = 0  # TODO calculate this
    return scrblk, crc_result, payload, lsbotfsfn, hrf, msbidxoffset
