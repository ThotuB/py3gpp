# Ref: TS 38.211 Section 6.3.2
from __future__ import annotations

from typing import Literal, Sequence

import numpy as np
from numpy.typing import NDArray

from py3gpp.dl.ofdm import nrCarrierConfig
from py3gpp.plc.sym import nrLowPAPRS, nrPRBS, nrSymbolModulate, nrTransformPrecode

# ---------------------------------------------------------------------------
# Shared helpers (hopping, scrambling, PRB sets)
# ---------------------------------------------------------------------------


def _prbSetTwoHops(
    prbset: Sequence[int],
    freqHopping: Literal["neither", "intraSlot", "interSlot"],
    secondHopStartPRB: int,
    nslot: int,
) -> NDArray[np.int_]:
    """TS 38.211: resolves the PRB set for each of the 2 hops in a slot."""
    prbsetArr = np.asarray(prbset, dtype=int)
    out = np.zeros((2, len(prbsetArr)), dtype=int)

    hop1 = prbsetArr.copy()
    if freqHopping == "interSlot" and nslot % 2 == 1:
        hop1 = prbsetArr - prbsetArr[0] + secondHopStartPRB

    out[0, :] = hop1
    if freqHopping == "intraSlot":
        out[1, :] = prbsetArr - prbsetArr[0] + secondHopStartPRB
    else:
        out[1, :] = hop1
    return out


def nrPUCCHHoppingInfo(
    cp: Literal["normal", "extended"],
    nslot: int,
    nid: int,
    groupHopping: Literal["neither", "enable", "disable"],
    initialCS: int,
    seqCS: int,
) -> dict:
    """PUCCH hopping structural information (TS 38.211 Section 6.3.2.2)."""
    assert cp in ("normal", "extended"), "The value must be 'normal' or 'extended'"
    assert 0 <= nid <= 1023, "The value must be 0..1023"
    assert groupHopping in ("neither", "enable", "disable"), "The value must be 'neither', 'enable', or 'disable'"
    assert 0 <= initialCS <= 11, "The value must be 0..11"
    assert 0 <= seqCS <= 11, "The value must be 0..11"

    nSlotSymb = 12 if cp == "extended" else 14
    m0, mcs = initialCS, seqCS

    weights8 = 2 ** np.arange(8)
    v = np.zeros(2, dtype=int)
    fgh = np.zeros(2, dtype=int)
    if groupHopping == "neither":
        hopping: Literal["neither", "groupHopping", "sequenceHopping"] = "neither"
    elif groupHopping == "enable":
        cinit = nid // 30
        offset = 8 * 2 * nslot
        prbs = nrPRBS(cinit, offset + 16)[offset:]
        fgh[:] = (weights8 @ prbs.reshape(8, 2, order="F")) % 30
        hopping = "groupHopping"
    else:
        cinit = 32 * (nid // 30) + (nid % 30)
        offset = 2 * nslot
        v[:] = nrPRBS(cinit, offset + 2)[offset:]
        hopping = "sequenceHopping"

    fss = nid % 30
    u = (fgh + fss) % 30

    offsetNcs = nSlotSymb * 8 * nslot
    prbsNcs = nrPRBS(nid, offsetNcs + nSlotSymb * 8)[offsetNcs:]
    ncs = weights8 @ prbsNcs.reshape(8, nSlotSymb, order="F")

    nRBSC = 12
    alpha = 2 * np.pi * ((m0 + mcs + ncs) % nRBSC) / nRBSC

    return {"U": u, "V": v, "Alpha": alpha, "FGH": fgh, "FSS": fss, "Hopping": hopping, "NCS": ncs}


def nrPUCCHPRBS(nid: int, rnti: int, length: int) -> NDArray[np.int32]:
    """Generate PUCCH scrambling sequence."""
    cinit = rnti * 2**15 + nid
    return nrPRBS(cinit, length)


# ---------------------------------------------------------------------------
# Format 0
# ---------------------------------------------------------------------------

_CS_TABLE_1BIT = np.array([[0, 6], [3, 9]])
_CS_TABLE_2BIT = np.array([[0, 3, 9, 6], [1, 4, 10, 7]])


def nrPUCCH0(
    ack: Sequence[int],
    sr: Sequence[int],
    symAllocation: Sequence[int],
    cp: Literal["normal", "extended"],
    nslot: int,
    nid: int,
    groupHopping: Literal["neither", "enable", "disable"],
    initialCS: int,
    freqHopping: Literal["enabled", "disabled"],
    mrb: int = 1,
) -> NDArray[np.complex128]:
    """Generate PUCCH format 0 symbols."""
    ackArr = np.asarray(ack, dtype=int).ravel()
    srArr = np.asarray(sr, dtype=int).ravel()
    symStart, nPUCCHSym = int(symAllocation[0]), int(symAllocation[1])

    if len(ackArr) == 0 and (len(srArr) == 0 or srArr[0] == 0):
        return np.zeros(0, dtype=np.complex128)

    csTable = _CS_TABLE_1BIT if len(ackArr) == 1 else _CS_TABLE_2BIT
    if len(ackArr) == 0:
        seqCS = int(csTable[0, 0])
    else:
        uciValue = int(ackArr[0]) if len(ackArr) == 1 else int(ackArr[0]) * 2 + int(ackArr[1])
        row = 0 if (len(srArr) == 0 or srArr[0] == 0) else 1
        seqCS = int(csTable[row, uciValue])

    info = nrPUCCHHoppingInfo(cp, nslot, nid, groupHopping, initialCS, seqCS)

    Msc = mrb * 12
    symRange = symStart + np.arange(nPUCCHSym)
    alpha = info["Alpha"][symRange]

    lps = nrLowPAPRS(int(info["U"][0]), int(info["V"][0]), alpha, Msc)
    if freqHopping == "enabled" and nPUCCHSym == 2:
        lps1 = nrLowPAPRS(int(info["U"][1]), int(info["V"][1]), float(info["Alpha"][symStart + 1]), Msc)
        return np.concatenate([lps[:, 0], lps1])
    return lps.ravel(order="F")


# ---------------------------------------------------------------------------
# Format 1
# ---------------------------------------------------------------------------


# TS 38.211 Section 6.3.2.4.1: PUCCH format 1 block-wise spreading phase tables, indexed by
# spreading factor nSF (1-7); row occi gives the phase index (in units of 2*pi/nSF) per symbol.
# Not a simple DFT matrix for composite nSF (e.g. nSF=4) -- must match these tables exactly.
_PUCCH1_PHI_TABLES: dict[int, NDArray[np.int_]] = {
    1: np.array([[0]]),
    2: np.array([[0, 0], [0, 1]]),
    3: np.array([[0, 0, 0], [0, 1, 2], [0, 2, 1]]),
    4: np.array([[0, 0, 0, 0], [0, 2, 0, 2], [0, 0, 2, 2], [0, 2, 2, 0]]),
    5: np.array(
        [
            [0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4],
            [0, 2, 4, 1, 3],
            [0, 3, 1, 4, 2],
            [0, 4, 3, 2, 1],
        ]
    ),
    6: np.array(
        [
            [0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5],
            [0, 2, 4, 0, 2, 4],
            [0, 3, 0, 3, 0, 3],
            [0, 4, 2, 0, 4, 2],
            [0, 5, 4, 3, 2, 1],
        ]
    ),
    7: np.array(
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 1, 2, 3, 4, 5, 6],
            [0, 2, 4, 6, 1, 3, 5],
            [0, 3, 6, 2, 5, 1, 4],
            [0, 4, 1, 5, 2, 6, 3],
            [0, 5, 3, 1, 6, 4, 2],
            [0, 6, 5, 4, 3, 2, 1],
        ]
    ),
}


def _pucch1Spreading(nSF: int, occi: int) -> NDArray[np.complex128]:
    """TS 38.211 6.3.2.4.1: PUCCH format 1 block-wise spreading orthogonal sequence."""
    assert 1 <= nSF <= 7, "nSF must be 1..7"
    assert 0 <= occi < nSF, "occi must be 0..nSF-1"
    phi = _PUCCH1_PHI_TABLES[nSF][occi, :]
    return np.exp(1j * 2 * np.pi * phi / nSF)


def nrPUCCH1(
    ack: Sequence[int],
    sr: Sequence[int],
    symAllocation: Sequence[int],
    cp: Literal["normal", "extended"],
    nslot: int,
    nid: int,
    groupHopping: Literal["neither", "enable", "disable"],
    initialCS: int,
    freqHopping: Literal["enabled", "disabled"],
    occi: int,
    mrb: int = 1,
) -> NDArray[np.complex128]:
    """Generate PUCCH format 1 symbols."""
    ackArr = np.asarray(ack, dtype=int).ravel()
    srArr = np.asarray(sr, dtype=int).ravel()

    if len(ackArr) == 0 and (len(srArr) == 0 or srArr[0] == 0):
        return np.zeros(0, dtype=np.complex128)

    symStart, nPUCCHSym = int(symAllocation[0]), int(symAllocation[1])

    uciIn = np.array([0]) if len(ackArr) == 0 else ackArr
    if len(uciIn) == 2:
        d = (1 / np.sqrt(2)) * ((1 - 2 * uciIn[0]) + 1j * (1 - 2 * uciIn[1]))
    else:
        d = (1 / np.sqrt(2)) * ((1 - 2 * uciIn[0]) + 1j * (1 - 2 * uciIn[0]))

    info = nrPUCCHHoppingInfo(cp, nslot, nid, groupHopping, initialCS, 0)

    nSF0 = nPUCCHSym // 2 if freqHopping == "disabled" else nPUCCHSym // 4
    nSF1 = nPUCCHSym // 2 - nSF0

    Msc = mrb * 12
    dataSymbols = symStart + 1 + 2 * np.arange(nSF0 + nSF1)

    alpha0 = info["Alpha"][dataSymbols[:nSF0]]
    lps1 = nrLowPAPRS(int(info["U"][0]), int(info["V"][0]), alpha0, Msc)

    assert occi < nSF0, "occi must be < nSF0"
    oSeq1 = _pucch1Spreading(nSF0, occi)

    if freqHopping == "enabled":
        alpha1 = info["Alpha"][dataSymbols[nSF0 : nSF0 + nSF1]]
        lps2 = nrLowPAPRS(int(info["U"][1]), int(info["V"][1]), alpha1, Msc)
        r = np.concatenate([lps1, lps2], axis=1)
        oSeq2 = _pucch1Spreading(nSF1, occi)
        oSeq = np.concatenate([oSeq1, oSeq2])
    else:
        r = lps1
        oSeq = oSeq1

    y = d * r
    return (y * oSeq).ravel(order="F")


# ---------------------------------------------------------------------------
# Format 2
# ---------------------------------------------------------------------------


def nrPUCCH2(uciCW: NDArray[np.int_], nid: int, rnti: int) -> NDArray[np.complex128]:
    """Generate PUCCH format 2 symbols."""
    uciCW = np.asarray(uciCW, dtype=int).ravel()
    c = nrPUCCHPRBS(nid, rnti, len(uciCW))
    btilde = np.bitwise_xor(uciCW, c)
    return nrSymbolModulate(btilde, "QPSK")


# ---------------------------------------------------------------------------
# Format 3
# ---------------------------------------------------------------------------


def nrPUCCH3(
    uciCW: NDArray[np.int_],
    modulation: Literal["QPSK", "pi/2-BPSK"],
    nid: int,
    rnti: int,
    mrb: int,
) -> NDArray[np.complex128]:
    """Generate PUCCH format 3 symbols."""
    uciCW = np.asarray(uciCW, dtype=int).ravel()
    c = nrPUCCHPRBS(nid, rnti, len(uciCW))
    btilde = np.bitwise_xor(uciCW, c)
    d = nrSymbolModulate(btilde, modulation)
    return nrTransformPrecode(d, mrb)


# ---------------------------------------------------------------------------
# Format 4
# ---------------------------------------------------------------------------

_BLOCKWISE_SPREAD_SF2 = np.array([[1, 1], [1, -1]])
_BLOCKWISE_SPREAD_SF4 = np.array([[1, 1, 1, 1], [1, -1j, -1, 1j], [1, -1, 1, -1], [1, 1j, -1, -1j]])


def _blockWiseSpreadingSequence(sf: Literal[2, 4], occi: int) -> NDArray[np.complex128]:
    """TS 38.211 Table 6.3.2.6.3-1/-2."""
    table = _BLOCKWISE_SPREAD_SF2 if sf == 2 else _BLOCKWISE_SPREAD_SF4
    return table[occi, :]


def _blockWiseSpread(d: NDArray[np.complex128], mrb: int, sf: Literal[2, 4], occi: int) -> NDArray[np.complex128]:
    """TS 38.211 Section 6.3.2.6.3: blockwise spreading for PUCCH formats 3/4."""
    Msc = mrb * 12
    wn = _blockWiseSpreadingSequence(sf, occi)
    w = np.repeat(wn, Msc // sf)

    nSymbols = sf * len(d) // Msc
    y = np.zeros(sf * len(d), dtype=np.complex128)
    k = np.arange(Msc)
    for l in range(nSymbols):
        y[l * Msc + k] = w * d[l * (Msc // sf) + (k % (Msc // sf))]
    return y


def nrPUCCH4(
    uciCW: NDArray[np.int_],
    modulation: Literal["QPSK", "pi/2-BPSK"],
    nid: int,
    rnti: int,
    sf: Literal[2, 4],
    occi: int,
    mrb: int = 1,
) -> NDArray[np.complex128]:
    """Generate PUCCH format 4 symbols."""
    assert sf in (2, 4), "sf must be 2 or 4"
    assert 0 <= occi < sf, "occi must be 0..sf-1"

    uciCW = np.asarray(uciCW, dtype=int).ravel()
    c = nrPUCCHPRBS(nid, rnti, len(uciCW))
    btilde = np.bitwise_xor(uciCW, c)
    d = nrSymbolModulate(btilde, modulation)
    y = _blockWiseSpread(d, mrb, sf, occi)
    return nrTransformPrecode(y, mrb)


# ---------------------------------------------------------------------------
# Config classes
# ---------------------------------------------------------------------------


class _PUCCHCommonConfig:
    def __init__(self) -> None:
        self._NSizeBWP: int | None = None
        self._NStartBWP: int | None = None
        self._SymbolAllocation: list[int] = [13, 1]
        self._PRBSet: list[int] = [0]
        self._FrequencyHopping: Literal["neither", "intraSlot", "interSlot"] = "neither"
        self._SecondHopStartPRB: int = 1
        self._Interlacing: bool = False
        self._RBSetIndex: int = 0
        self._InterlaceIndex: int = 0

    @property
    def NSizeBWP(self) -> int | None:
        return self._NSizeBWP

    @NSizeBWP.setter
    def NSizeBWP(self, value: int) -> None:
        assert 1 <= value <= 275, "The value must be 1..275"
        self._NSizeBWP = value

    @property
    def NStartBWP(self) -> int | None:
        return self._NStartBWP

    @NStartBWP.setter
    def NStartBWP(self, value: int) -> None:
        assert 0 <= value <= 2473, "The value must be 0..2473"
        self._NStartBWP = value

    @property
    def SymbolAllocation(self) -> list[int]:
        return self._SymbolAllocation

    @SymbolAllocation.setter
    def SymbolAllocation(self, value: list[int]) -> None:
        assert len(value) == 2, "The value must be [startSymbol, numSymbols]"
        self._SymbolAllocation = value

    @property
    def PRBSet(self) -> list[int]:
        return self._PRBSet

    @PRBSet.setter
    def PRBSet(self, value: list[int]) -> None:
        assert min(value) >= 0 and max(value) <= 274, "The value must be 0..274"
        self._PRBSet = value

    @property
    def FrequencyHopping(self) -> Literal["neither", "intraSlot", "interSlot"]:
        return self._FrequencyHopping

    @FrequencyHopping.setter
    def FrequencyHopping(self, value: Literal["neither", "intraSlot", "interSlot"]) -> None:
        assert value in (
            "neither",
            "intraSlot",
            "interSlot",
        ), "The value must be 'neither', 'intraSlot', or 'interSlot'"
        self._FrequencyHopping = value

    @property
    def SecondHopStartPRB(self) -> int:
        return self._SecondHopStartPRB

    @SecondHopStartPRB.setter
    def SecondHopStartPRB(self, value: int) -> None:
        assert 0 <= value <= 274, "The value must be 0..274"
        self._SecondHopStartPRB = value

    @property
    def Interlacing(self) -> bool:
        return self._Interlacing

    @Interlacing.setter
    def Interlacing(self, value: bool) -> None:
        self._Interlacing = value

    @property
    def RBSetIndex(self) -> int:
        return self._RBSetIndex

    @RBSetIndex.setter
    def RBSetIndex(self, value: int) -> None:
        self._RBSetIndex = value

    @property
    def InterlaceIndex(self) -> int:
        return self._InterlaceIndex

    @InterlaceIndex.setter
    def InterlaceIndex(self, value: int) -> None:
        self._InterlaceIndex = value


class _PUCCHHoppingConfigBase(_PUCCHCommonConfig):
    def __init__(self) -> None:
        super().__init__()
        self._GroupHopping: Literal["neither", "enable", "disable"] = "neither"
        self._HoppingID: int | None = None
        self._InitialCyclicShift: int = 0

    @property
    def GroupHopping(self) -> Literal["neither", "enable", "disable"]:
        return self._GroupHopping

    @GroupHopping.setter
    def GroupHopping(self, value: Literal["neither", "enable", "disable"]) -> None:
        assert value in ("neither", "enable", "disable"), "The value must be 'neither', 'enable', or 'disable'"
        self._GroupHopping = value

    @property
    def HoppingID(self) -> int | None:
        return self._HoppingID

    @HoppingID.setter
    def HoppingID(self, value: int) -> None:
        assert 0 <= value <= 1023, "The value must be 0..1023"
        self._HoppingID = value

    @property
    def InitialCyclicShift(self) -> int:
        return self._InitialCyclicShift

    @InitialCyclicShift.setter
    def InitialCyclicShift(self, value: int) -> None:
        assert 0 <= value <= 11, "The value must be 0..11"
        self._InitialCyclicShift = value


class nrPUCCH0Config(_PUCCHHoppingConfigBase):
    """PUCCH format 0 configuration parameters."""


class nrPUCCH1Config(_PUCCHHoppingConfigBase):
    """PUCCH format 1 configuration parameters."""

    def __init__(self) -> None:
        super().__init__()
        self._SymbolAllocation = [0, 14]
        self._OCCI: int = 0

    @property
    def OCCI(self) -> int:
        return self._OCCI

    @OCCI.setter
    def OCCI(self, value: int) -> None:
        assert 0 <= value <= 6, "The value must be 0..6"
        self._OCCI = value


class nrPUCCH2Config(_PUCCHCommonConfig):
    """PUCCH format 2 configuration parameters."""

    def __init__(self) -> None:
        super().__init__()
        self._NID: int | None = None
        self._RNTI: int = 1

    @property
    def NID(self) -> int | None:
        return self._NID

    @NID.setter
    def NID(self, value: int) -> None:
        assert 0 <= value <= 1023, "The value must be 0..1023"
        self._NID = value

    @property
    def RNTI(self) -> int:
        return self._RNTI

    @RNTI.setter
    def RNTI(self, value: int) -> None:
        assert 0 <= value <= 65535, "The value must be 0..65535"
        self._RNTI = value


class nrPUCCH3Config:
    """PUCCH format 3 configuration parameters (generation-relevant fields only)."""

    def __init__(self) -> None:
        self._NID: int | None = None
        self._RNTI: int = 1
        self._Modulation: Literal["QPSK", "pi/2-BPSK"] = "QPSK"

    @property
    def NID(self) -> int | None:
        return self._NID

    @NID.setter
    def NID(self, value: int) -> None:
        assert 0 <= value <= 1023, "The value must be 0..1023"
        self._NID = value

    @property
    def RNTI(self) -> int:
        return self._RNTI

    @RNTI.setter
    def RNTI(self, value: int) -> None:
        assert 0 <= value <= 65535, "The value must be 0..65535"
        self._RNTI = value

    @property
    def Modulation(self) -> Literal["QPSK", "pi/2-BPSK"]:
        return self._Modulation

    @Modulation.setter
    def Modulation(self, value: Literal["QPSK", "pi/2-BPSK"]) -> None:
        assert value in ("QPSK", "pi/2-BPSK"), "The value must be 'QPSK' or 'pi/2-BPSK'"
        self._Modulation = value


class nrPUCCH4Config(nrPUCCH3Config):
    """PUCCH format 4 configuration parameters (generation-relevant fields only)."""

    def __init__(self) -> None:
        super().__init__()
        self._SpreadingFactor: Literal[2, 4] = 2
        self._OCCI: int = 0

    @property
    def SpreadingFactor(self) -> Literal[2, 4]:
        return self._SpreadingFactor

    @SpreadingFactor.setter
    def SpreadingFactor(self, value: Literal[2, 4]) -> None:
        assert value in (2, 4), "The value must be 2 or 4"
        self._SpreadingFactor = value

    @property
    def OCCI(self) -> int:
        return self._OCCI

    @OCCI.setter
    def OCCI(self, value: int) -> None:
        assert 0 <= value < self._SpreadingFactor, "The value must be 0..SpreadingFactor-1"
        self._OCCI = value


# ---------------------------------------------------------------------------
# Resource element indices (Formats 0, 1, 2 only)
# ---------------------------------------------------------------------------


def nrPUCCHIndices(
    carrier: nrCarrierConfig, pucch: nrPUCCH0Config | nrPUCCH1Config | nrPUCCH2Config
) -> NDArray[np.int_]:
    """Generate PUCCH resource element indices (formats 0, 1, and 2 only)."""
    if isinstance(pucch, (nrPUCCH3Config, nrPUCCH4Config)):
        raise NotImplementedError("PUCCH formats 3/4 resource mapping is not yet implemented")
    if pucch.Interlacing:
        raise NotImplementedError("Interlacing is not yet implemented")

    NSizeBWP = carrier.NSizeGrid if pucch.NSizeBWP is None else pucch.NSizeBWP
    NStartBWP = carrier.NStartGrid if pucch.NStartBWP is None else pucch.NStartBWP

    nRBSC = 12
    nslot = carrier.NSlot % carrier.SlotsPerFrame
    prbsetHop = _prbSetTwoHops(pucch.PRBSet, pucch.FrequencyHopping, pucch.SecondHopStartPRB, nslot)
    intraSlotFreqHopping = pucch.FrequencyHopping == "intraSlot"

    symStart, numSym = int(pucch.SymbolAllocation[0]), int(pucch.SymbolAllocation[1])

    if isinstance(pucch, nrPUCCH1Config):
        scInd = np.arange(nRBSC)
        lsymFull = symStart + np.arange(numSym)
        dataSymbols = lsymFull[1::2]  # every other symbol, excluding the DM-RS symbol at index 0
        numSymUCI = len(dataSymbols)
        nSF0 = numSym // 4 if intraSlotFreqHopping else numSymUCI
        hopAssignment = [0] * nSF0 + [1] * (numSymUCI - nSF0)
        lsym = dataSymbols
    else:
        scInd = np.arange(nRBSC) if isinstance(pucch, nrPUCCH0Config) else np.array([0, 2, 3, 5, 6, 8, 9, 11])
        lsym = symStart + np.arange(numSym)
        hopAssignment = [min(col, 1) for col in range(numSym)]

    K = np.stack([(nRBSC * prbsetHop[hop][:, None] + scInd[None, :]).ravel() for hop in hopAssignment], axis=1)
    L = np.tile(lsym, (K.shape[0], 1))

    totalSC = carrier.NSizeGrid * nRBSC
    indices = (NStartBWP * nRBSC + K) + L * totalSC
    return indices.ravel(order="F")
