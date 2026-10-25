# Ref: TS 38.211 Section 7.4.1.7
from __future__ import annotations

from typing import Literal, Sequence

import numpy as np
from numpy.typing import NDArray

from py3gpp.dl.ofdm import nrCarrierConfig
from py3gpp.plc.sym import nrPRBS, nrSymbolModulate

# TS 38.211 Table 7.4.1.7.3-1: frequency offset values k', indexed by CombSize and
# PRS OFDM symbol number l' (0..11), cycled modulo 12 for longer resources.
_FREQ_OFFSET_TABLE: dict[int, NDArray[np.int_]] = {
    2: np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]),
    4: np.array([0, 2, 1, 3, 0, 2, 1, 3, 0, 2, 1, 3]),
    6: np.array([0, 3, 1, 4, 2, 5, 0, 3, 1, 4, 2, 5]),
    12: np.array([0, 6, 3, 9, 1, 7, 4, 10, 2, 8, 5, 11]),
}


class nrPRSConfig:
    """PRS configuration parameters (TS 38.211 Section 7.4.1.7)."""

    def __init__(self) -> None:
        self._PRSResourceSetPeriod: Literal["on", "off"] | list[int] = "on"
        self._PRSResourceOffset: list[int] = [0]
        self._PRSResourceRepetition: int = 1
        self._PRSResourceTimeGap: int = 1
        self._MutingPattern1: list[int] = []
        self._MutingBitRepetition: int = 1
        self._MutingPattern2: list[int] = []
        self._NumPRSSymbols: list[int] = [12]
        self._SymbolStart: list[int] = [0]
        self._NumRB: int = 52
        self._RBOffset: int = 0
        self._CombSize: Literal[2, 4, 6, 12] = 2
        self._REOffset: list[int] = [0]
        self._NPRSID: list[int] = [0]

    @property
    def PRSResourceSetPeriod(self) -> Literal["on", "off"] | list[int]:
        return self._PRSResourceSetPeriod

    @PRSResourceSetPeriod.setter
    def PRSResourceSetPeriod(self, value: Literal["on", "off"] | Sequence[int]) -> None:
        if isinstance(value, str):
            assert value in ("on", "off"), "The value must be 'on', 'off', or [period, offset]"
            self._PRSResourceSetPeriod = value
        else:
            assert len(value) == 2, "The value must be [period, offset]"
            self._PRSResourceSetPeriod = list(value)

    @property
    def PRSResourceOffset(self) -> list[int]:
        return self._PRSResourceOffset

    @PRSResourceOffset.setter
    def PRSResourceOffset(self, value: int | Sequence[int]) -> None:
        values = [value] if isinstance(value, int) else list(value)
        assert all(0 <= v <= 511 for v in values), "The value must be 0..511"
        self._PRSResourceOffset = values

    @property
    def PRSResourceRepetition(self) -> int:
        return self._PRSResourceRepetition

    @PRSResourceRepetition.setter
    def PRSResourceRepetition(self, value: int) -> None:
        assert value in (1, 2, 4, 6, 8, 16, 32), "The value must be one of 1,2,4,6,8,16,32"
        self._PRSResourceRepetition = value

    @property
    def PRSResourceTimeGap(self) -> int:
        return self._PRSResourceTimeGap

    @PRSResourceTimeGap.setter
    def PRSResourceTimeGap(self, value: int) -> None:
        assert value in (1, 2, 4, 8, 16, 32), "The value must be one of 1,2,4,8,16,32"
        self._PRSResourceTimeGap = value

    @property
    def MutingPattern1(self) -> list[int]:
        return self._MutingPattern1

    @MutingPattern1.setter
    def MutingPattern1(self, value: Sequence[int]) -> None:
        self._MutingPattern1 = list(value)

    @property
    def MutingBitRepetition(self) -> int:
        return self._MutingBitRepetition

    @MutingBitRepetition.setter
    def MutingBitRepetition(self, value: int) -> None:
        assert value in (1, 2, 4, 8), "The value must be one of 1,2,4,8"
        self._MutingBitRepetition = value

    @property
    def MutingPattern2(self) -> list[int]:
        return self._MutingPattern2

    @MutingPattern2.setter
    def MutingPattern2(self, value: Sequence[int]) -> None:
        self._MutingPattern2 = list(value)

    @property
    def NumPRSSymbols(self) -> list[int]:
        return self._NumPRSSymbols

    @NumPRSSymbols.setter
    def NumPRSSymbols(self, value: int | Sequence[int]) -> None:
        values = [value] if isinstance(value, int) else list(value)
        assert all(0 <= v <= 12 for v in values), "The value must be 0..12"
        self._NumPRSSymbols = values

    @property
    def SymbolStart(self) -> list[int]:
        return self._SymbolStart

    @SymbolStart.setter
    def SymbolStart(self, value: int | Sequence[int]) -> None:
        values = [value] if isinstance(value, int) else list(value)
        assert all(0 <= v <= 13 for v in values), "The value must be 0..13"
        self._SymbolStart = values

    @property
    def NumRB(self) -> int:
        return self._NumRB

    @NumRB.setter
    def NumRB(self, value: int) -> None:
        assert 0 <= value <= 275, "The value must be 0..275"
        self._NumRB = value

    @property
    def RBOffset(self) -> int:
        return self._RBOffset

    @RBOffset.setter
    def RBOffset(self, value: int) -> None:
        assert 0 <= value <= 274, "The value must be 0..274"
        self._RBOffset = value

    @property
    def CombSize(self) -> Literal[2, 4, 6, 12]:
        return self._CombSize

    @CombSize.setter
    def CombSize(self, value: Literal[2, 4, 6, 12]) -> None:
        assert value in (2, 4, 6, 12), "The value must be one of 2,4,6,12"
        self._CombSize = value

    @property
    def REOffset(self) -> list[int]:
        return self._REOffset

    @REOffset.setter
    def REOffset(self, value: int | Sequence[int]) -> None:
        values = [value] if isinstance(value, int) else list(value)
        assert all(0 <= v < self._CombSize for v in values), "The value must be 0..CombSize-1"
        self._REOffset = values

    @property
    def NPRSID(self) -> list[int]:
        return self._NPRSID

    @NPRSID.setter
    def NPRSID(self, value: int | Sequence[int]) -> None:
        values = [value] if isinstance(value, int) else list(value)
        assert all(0 <= v <= 4095 for v in values), "The value must be 0..4095"
        self._NPRSID = values


def _scalarExpand(values: list[int], numRes: int) -> NDArray[np.int_]:
    arr = np.asarray(values, dtype=int)
    if len(arr) == 1:
        return np.full(numRes, arr[0])
    return arr


def _schedulePRS(carrier: nrCarrierConfig, prs: nrPRSConfig) -> tuple[NDArray[np.bool_], int, int]:
    """Direct port of nr5g.internal.validateAndSchedulePRS's scheduling logic."""
    numRes = max(
        len(prs.PRSResourceOffset), len(prs.NumPRSSymbols), len(prs.SymbolStart), len(prs.REOffset), len(prs.NPRSID)
    )

    nFrame = carrier.NFrame + carrier.NSlot // carrier.SlotsPerFrame
    nslot = carrier.NSlot % carrier.SlotsPerFrame
    nFrame = nFrame % 1024

    if isinstance(prs.PRSResourceSetPeriod, str):
        presence = np.full(numRes, prs.PRSResourceSetPeriod == "on")
        return presence, numRes, nslot

    tprsPer, tprsOffset = prs.PRSResourceSetPeriod
    tprsRep = prs.PRSResourceRepetition
    tprsGap = prs.PRSResourceTimeGap
    validOptions = tprsGap * np.arange(tprsRep)

    b1 = prs.MutingPattern1
    tprsMuting = prs.MutingBitRepetition
    b2 = prs.MutingPattern2
    L = len(b1)

    resOffsets = _scalarExpand(prs.PRSResourceOffset, numRes)

    presence = np.zeros(numRes, dtype=bool)
    for resIdx in range(numRes):
        temp = carrier.SlotsPerFrame * nFrame + nslot - tprsOffset - int(resOffsets[resIdx])
        prsCheck = temp % tprsPer
        check1 = prsCheck in validOptions

        bi1 = True
        bi2 = True
        if L > 0:
            i1 = (temp // (tprsMuting * tprsPer)) % L
            bi1 = bool(b1[i1])
        if len(b2) > 0:
            i2 = (prsCheck // tprsGap) % tprsRep
            bi2 = bool(b2[i2])
        presence[resIdx] = check1 and bi1 and bi2

    return presence, numRes, nslot


def nrPRS(carrier: nrCarrierConfig, prs: nrPRSConfig) -> NDArray[np.complex128]:
    """Generate PRS symbols (concatenated output across all resources)."""
    presence, numRes, nslot = _schedulePRS(carrier, prs)

    numREsPerRB = 12 // prs.CombSize
    mIndPerRB = np.arange(numREsPerRB)
    nCRB = prs.RBOffset + carrier.NStartGrid + np.arange(prs.NumRB)

    numPRSSymbols = _scalarExpand(prs.NumPRSSymbols, numRes)
    symbolStart = _scalarExpand(prs.SymbolStart, numRes)
    nprsidArr = _scalarExpand(prs.NPRSID, numRes)

    allSyms: list[NDArray[np.complex128]] = []
    for resIdx in range(numRes):
        LPRS = int(numPRSSymbols[resIdx])
        if not presence[resIdx] or LPRS == 0 or prs.NumRB == 0:
            continue

        nprsid = int(nprsidArr[resIdx])
        l = symbolStart[resIdx] + np.arange(LPRS)

        tempNprsid = nprsid % 1024
        cinit = (
            (2**22) * (nprsid // 1024)
            + (2**10) * (carrier.SymbolsPerSlot * nslot + l + 1) * (2 * tempNprsid + 1)
            + tempNprsid
        ) % (2**31)

        mValuesPerRB = (mIndPerRB[:, None] + nCRB[None, :] * numREsPerRB).ravel(order="F")
        bitsTotal = 2 * (int(mValuesPerRB[-1]) + 1)
        bitStart = 2 * int(mValuesPerRB[0])

        c = np.zeros((bitsTotal - bitStart, LPRS), dtype=int)
        for lIdx in range(LPRS):
            cFull = nrPRBS(int(cinit[lIdx]), bitsTotal)
            c[:, lIdx] = cFull[bitStart:bitsTotal]

        allSyms.append(nrSymbolModulate(c.ravel(order="F"), "QPSK"))

    if not allSyms:
        return np.zeros(0, dtype=np.complex128)
    return np.concatenate(allSyms)


def nrPRSIndices(carrier: nrCarrierConfig, prs: nrPRSConfig) -> NDArray[np.int_]:
    """Generate PRS resource element indices (concatenated output across all resources)."""
    presence, numRes, _ = _schedulePRS(carrier, prs)

    nRBSC = 12
    KPRSComb = prs.CombSize
    numREsPerRB = nRBSC // KPRSComb
    mIndPerRB = np.arange(numREsPerRB)
    nStartGrid = carrier.NStartGrid
    nCRB = prs.RBOffset + nStartGrid + np.arange(prs.NumRB)
    m = (mIndPerRB[:, None] + nCRB[None, :] * numREsPerRB).ravel(order="F")

    totalSC = carrier.NSizeGrid * nRBSC

    numPRSSymbols = _scalarExpand(prs.NumPRSSymbols, numRes)
    symbolStart = _scalarExpand(prs.SymbolStart, numRes)
    reOffsetArr = _scalarExpand(prs.REOffset, numRes)

    kPrimeTable = _FREQ_OFFSET_TABLE[KPRSComb]

    allInd: list[NDArray[np.int_]] = []
    for resIdx in range(numRes):
        LPRS = int(numPRSSymbols[resIdx])
        if not presence[resIdx] or LPRS == 0 or prs.NumRB == 0:
            continue

        kPrime = kPrimeTable[np.arange(LPRS) % 12]
        kSubs = (m[:, None] * KPRSComb + (reOffsetArr[resIdx] + kPrime[None, :]) % KPRSComb) - nStartGrid * nRBSC
        lSubs = symbolStart[resIdx] + np.arange(LPRS)
        L = np.tile(lSubs, (kSubs.shape[0], 1))

        indices = kSubs + L * totalSC
        allInd.append(indices.ravel(order="F"))

    if not allInd:
        return np.zeros(0, dtype=int)
    return np.concatenate(allInd)
