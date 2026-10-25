# Ref: TS 38.212 Section 6.3.1
from __future__ import annotations

import itertools
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from py3gpp.plc.trs.crc import nrCRCDecode, nrCRCEncode
from py3gpp.plc.trs.polar import nrPolarDecode, nrPolarEncode, nrRateMatchPolar, nrRateRecoverPolar

# TS 38.212 Table 5.3.3.3-1: basis sequences for 3-11 bit Reed-Muller-like encoding.
_BASIS_SEQ_311 = np.array(
    [
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1],
        [1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1],
        [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1],
        [1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1],
        [1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1],
        [1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1],
        [1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1],
        [1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1],
        [1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1],
        [1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1],
        [1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0],
        [1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0],
        [1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
        [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1],
        [1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0],
        [1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0],
        [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0],
        [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
)

_QM = {"PI/2-BPSK": 1, "BPSK": 1, "QPSK": 2, "16QAM": 4, "64QAM": 6, "256QAM": 8}


def _getQm(modulation: str) -> int:
    return _QM[modulation.upper()]


def _getN(K: int, E: int, nmax: int) -> int:
    """TS 38.212 Section 5.3.1 mother-code-size selection."""
    cl2e = int(np.ceil(np.log2(E)))
    if E <= (9 / 8) * 2 ** (cl2e - 1) and K / E < 9 / 16:
        n1 = cl2e - 1
    else:
        n1 = cl2e

    rmin = 1 / 8
    n2 = int(np.ceil(np.log2(K / rmin)))

    nmin = 5
    n = max(min(n1, n2, nmax), nmin)
    return 2**n


def _resolvePolarN(K: int, euci: int) -> Literal[9, 10]:
    """Resolve the Polar nmax for the A>=12 UCI path, gated by two pre-existing limitations in
    this repo's Polar infra (plc/trs/polar.py): nrPolarDecode only supports nmax in {9, 10}, and
    nrRateMatchPolar/nrRateRecoverPolar only support repetition (N <= E), not
    puncturing/shortening. TS 38.212's own formula can legitimately pick nmax as low as 5 (e.g.
    for the whole A=12..19, 6-bit-CRC range, which always resolves to nmax=8) -- those
    combinations are out of scope until the underlying Polar infra supports them.
    """
    N = _getN(K, euci, 10)
    nmax = int(np.log2(N))
    if nmax not in (9, 10):
        raise NotImplementedError(
            f"this (A, Euci) combination requires Polar nmax={nmax}, but nrPolarDecode only "
            "supports nmax in {9, 10} (pre-existing limitation)"
        )
    if N > euci:
        raise NotImplementedError("shortening/puncturing (N > Euci) is not yet implemented")
    return nmax


def _softCombine(llrs: NDArray[np.floating], N: int) -> NDArray[np.floating]:
    E = len(llrs)
    if E >= N:
        reps = int(np.ceil(E / N))
        padded = np.zeros(N * reps)
        padded[:E] = llrs
        return padded.reshape(N, reps, order="F").sum(axis=1)
    rec = np.zeros(N)
    rec[:E] = llrs
    return rec


def _smallEncode12(uciBits: NDArray[np.int_], modulation: str) -> NDArray[np.int_]:
    """TS 38.212 Sections 5.3.3.1/5.3.3.2: encode 1 or 2 bits. Placeholder bits "x"/"y" are -1/-2."""
    Qm = _getQm(modulation)
    x, y = -1, -2
    b = np.asarray(uciBits).astype(int)

    if len(b) == 1:
        if Qm == 1:
            return b.copy()
        return np.concatenate([b, [y], np.full(Qm - 2, x, dtype=int)])

    c2 = int(b[0]) ^ int(b[1])
    if Qm == 1:
        return np.concatenate([b, [c2]])

    base = np.concatenate([b, [c2]])
    ib = np.tile(base, 2).reshape(2, 3, order="F")
    xb = np.full((Qm - 2, 3), x, dtype=int)
    return np.vstack([ib, xb]).reshape(-1, order="F")


def _smallEncode311(uciBits: NDArray[np.int_]) -> NDArray[np.int_]:
    """TS 38.212 Section 5.3.3.3: encode 3-11 bits via the Table 5.3.3.3-1 basis sequences."""
    b = np.asarray(uciBits).astype(int)
    A = len(b)
    return (_BASIS_SEQ_311[:, :A] @ b) % 2


def _smallDecode12(uciLLRs: NDArray[np.floating], A: int, modulation: str) -> NDArray[np.int_]:
    Qm = _getQm(modulation)
    N = Qm if A == 1 else 3 * Qm
    rec = _softCombine(uciLLRs, N)

    bestDist, bestBits = np.inf, np.zeros(A, dtype=int)
    for candidate in itertools.product((0, 1), repeat=A):
        bits = np.array(candidate, dtype=int)
        enc = _smallEncode12(bits, modulation)
        enc[enc == -1] = 1
        yIdx = np.where(enc == -2)[0]
        enc[yIdx] = enc[yIdx - 1]
        soft = 1 - 2.0 * enc
        dist = np.sum(np.abs(rec - soft) ** 2) / np.sum(np.abs(soft) ** 2)
        if dist < bestDist:
            bestDist, bestBits = dist, bits
    return bestBits


def _smallDecode311(uciLLRs: NDArray[np.floating], A: int) -> NDArray[np.int_]:
    N = 32
    rec = _softCombine(uciLLRs, N)

    bestDist, bestBits = np.inf, np.zeros(A, dtype=int)
    for candidate in itertools.product((0, 1), repeat=A):
        bits = np.array(candidate, dtype=int)
        soft = 1 - 2.0 * _smallEncode311(bits)
        dist = np.sum(np.abs(rec - soft) ** 2) / np.sum(np.abs(soft) ** 2)
        if dist < bestDist:
            bestDist, bestBits = dist, bits
    return bestBits


def nrUCIEncode(uciBits: NDArray[np.int_], euci: int, modulation: str = "QPSK") -> NDArray[np.int_]:
    """Encode uplink control information (UCI)."""
    bits = np.asarray(uciBits).astype(int)
    A = len(bits)
    assert 1 <= A <= 1706, "The number of UCI bits must be 1..1706"

    if A >= 12:
        if A >= 1013 or (A >= 360 and euci >= 1088):
            raise NotImplementedError("two-codeword segmentation is not yet implemented")

        Lcrc: Literal["6", "11"] = "6" if A <= 19 else "11"
        bitsCRC = nrCRCEncode(bits, Lcrc)[:, 0]
        K = len(bitsCRC)

        nmax = _resolvePolarN(K, euci)
        encoded = nrPolarEncode(bitsCRC, euci, nmax=nmax, iil=False)
        return nrRateMatchPolar(encoded, K, euci, ibil=True)

    out = _smallEncode12(bits, modulation) if A < 3 else _smallEncode311(bits)
    N = len(out)
    return out[np.arange(euci) % N]


def nrUCIDecode(
    uciLLRs: NDArray[np.floating], A: int, modulation: str = "QPSK", listLength: int = 8
) -> tuple[NDArray[np.int_], bool]:
    """Decode uplink control information (UCI)."""
    assert 1 <= A <= 1706, "A must be 1..1706"
    euci = len(uciLLRs)

    if A >= 12:
        if A >= 1013 or (A >= 360 and euci >= 1088):
            raise NotImplementedError("two-codeword segmentation is not yet implemented")

        crclen: Literal[6, 11] = 6 if A <= 19 else 11
        Lcrc: Literal["6", "11"] = "6" if A <= 19 else "11"
        K = A + crclen

        nmax = _resolvePolarN(K, euci)
        recovered = nrRateRecoverPolar(uciLLRs, K, 2**nmax, ibil=True)
        decoded = nrPolarDecode(recovered, K, euci, listLength, nmax=nmax, iil=False, CRClen=crclen)
        decodedBits, err = nrCRCDecode(decoded, Lcrc)
        return decodedBits[:, 0], bool(err)

    bits = _smallDecode12(uciLLRs, A, modulation) if A < 3 else _smallDecode311(uciLLRs, A)
    return bits, False
