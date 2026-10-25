# Ref: TS 38.211 Section 6.4.1.4
from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from py3gpp.dl.ofdm import nrCarrierConfig
from py3gpp.plc.sym import nrLowPAPRS

# TS 38.211 Table 6.4.1.4.3-1: for each CSRS (row), 4 (mSRS, N) pairs for BSRS=0..3.
_BANDWIDTH_CONFIG_TABLE = np.array(
    [
        [4, 1, 4, 1, 4, 1, 4, 1],
        [8, 1, 4, 2, 4, 1, 4, 1],
        [12, 1, 4, 3, 4, 1, 4, 1],
        [16, 1, 4, 4, 4, 1, 4, 1],
        [16, 1, 8, 2, 4, 2, 4, 1],
        [20, 1, 4, 5, 4, 1, 4, 1],
        [24, 1, 4, 6, 4, 1, 4, 1],
        [24, 1, 12, 2, 4, 3, 4, 1],
        [28, 1, 4, 7, 4, 1, 4, 1],
        [32, 1, 16, 2, 8, 2, 4, 2],
        [36, 1, 12, 3, 4, 3, 4, 1],
        [40, 1, 20, 2, 4, 5, 4, 1],
        [48, 1, 16, 3, 8, 2, 4, 2],
        [48, 1, 24, 2, 12, 2, 4, 3],
        [52, 1, 4, 13, 4, 1, 4, 1],
        [56, 1, 28, 2, 4, 7, 4, 1],
        [60, 1, 20, 3, 4, 5, 4, 1],
        [64, 1, 32, 2, 16, 2, 4, 4],
        [72, 1, 24, 3, 12, 2, 4, 3],
        [72, 1, 36, 2, 12, 3, 4, 3],
        [76, 1, 4, 19, 4, 1, 4, 1],
        [80, 1, 40, 2, 20, 2, 4, 5],
        [88, 1, 44, 2, 4, 11, 4, 1],
        [96, 1, 32, 3, 16, 2, 4, 4],
        [96, 1, 48, 2, 24, 2, 4, 6],
        [104, 1, 52, 2, 4, 13, 4, 1],
        [112, 1, 56, 2, 28, 2, 4, 7],
        [120, 1, 60, 2, 20, 3, 4, 5],
        [120, 1, 40, 3, 8, 5, 4, 2],
        [120, 1, 24, 5, 12, 2, 4, 3],
        [128, 1, 64, 2, 32, 2, 4, 8],
        [128, 1, 64, 2, 16, 4, 4, 4],
        [128, 1, 16, 8, 8, 2, 4, 2],
        [132, 1, 44, 3, 4, 11, 4, 1],
        [136, 1, 68, 2, 4, 17, 4, 1],
        [144, 1, 72, 2, 36, 2, 4, 9],
        [144, 1, 48, 3, 24, 2, 12, 2],
        [144, 1, 48, 3, 16, 3, 4, 4],
        [144, 1, 16, 9, 8, 2, 4, 2],
        [152, 1, 76, 2, 4, 19, 4, 1],
        [160, 1, 80, 2, 40, 2, 4, 10],
        [160, 1, 80, 2, 20, 4, 4, 5],
        [160, 1, 32, 5, 16, 2, 4, 4],
        [168, 1, 84, 2, 28, 3, 4, 7],
        [176, 1, 88, 2, 44, 2, 4, 11],
        [184, 1, 92, 2, 4, 23, 4, 1],
        [192, 1, 96, 2, 48, 2, 4, 12],
        [192, 1, 96, 2, 24, 4, 4, 6],
        [192, 1, 64, 3, 16, 4, 4, 4],
        [192, 1, 24, 8, 8, 3, 4, 2],
        [208, 1, 104, 2, 52, 2, 4, 13],
        [216, 1, 108, 2, 36, 3, 4, 9],
        [224, 1, 112, 2, 56, 2, 4, 14],
        [240, 1, 120, 2, 60, 2, 4, 15],
        [240, 1, 80, 3, 20, 4, 4, 5],
        [240, 1, 48, 5, 16, 3, 8, 2],
        [240, 1, 24, 10, 12, 2, 4, 3],
        [256, 1, 128, 2, 64, 2, 4, 16],
        [256, 1, 128, 2, 32, 4, 4, 8],
        [256, 1, 16, 16, 8, 2, 4, 2],
        [264, 1, 132, 2, 44, 3, 4, 11],
        [272, 1, 136, 2, 68, 2, 4, 17],
        [272, 1, 68, 4, 4, 17, 4, 1],
        [272, 1, 16, 17, 8, 2, 4, 2],
    ]
)

_NCS_MAX = {2: 8, 4: 12, 8: 6}


def _srsBandwidthConfig(csrs: int, bsrs: int) -> tuple[int, int]:
    """TS 38.211 Table 6.4.1.4.3-1: returns (mSRS, N) for the given CSRS/BSRS."""
    row = _BANDWIDTH_CONFIG_TABLE[csrs]
    return int(row[2 * bsrs]), int(row[2 * bsrs + 1])


class nrSRSConfig:
    """SRS configuration parameters."""

    def __init__(self) -> None:
        self._NumSRSPorts: Literal[1, 2, 4, 8] = 1
        self._SymbolStart: int = 13
        self._NumSRSSymbols: Literal[1, 2, 4, 8, 10, 12, 14] = 1
        self._CSRS: int = 0
        self._BSRS: Literal[0, 1, 2, 3] = 0
        self._BHop: Literal[0, 1, 2, 3] = 0
        self._KTC: Literal[2, 4, 8] = 2
        self._KBarTC: int = 0
        self._CyclicShift: int = 0
        self._NSRSID: int = 0
        self._FrequencyStart: int = 0
        self._NRRC: int = 0
        self._SRSPeriod: Literal["on", "off"] | list[int] = "on"
        self._GroupSeqHopping: Literal["neither", "groupHopping", "sequenceHopping"] = "neither"
        self._ResourceType: Literal["periodic", "semi-persistent", "aperiodic"] = "periodic"
        self._EnableEightPortTDM: bool = False
        self._CombOffsetHopping: bool = False
        self._CyclicShiftHopping: bool = False
        self._SRSPositioning: bool = False
        self._FrequencyScalingFactor: Literal[1, 2, 4] = 1

    @property
    def NumSRSPorts(self) -> Literal[1, 2, 4, 8]:
        return self._NumSRSPorts

    @NumSRSPorts.setter
    def NumSRSPorts(self, value: Literal[1, 2, 4, 8]) -> None:
        assert value in (1, 2, 4, 8), "The value must be 1, 2, 4, or 8"
        self._NumSRSPorts = value

    @property
    def SymbolStart(self) -> int:
        return self._SymbolStart

    @SymbolStart.setter
    def SymbolStart(self, value: int) -> None:
        assert 0 <= value <= 13, "The value must be 0..13"
        self._SymbolStart = value

    @property
    def NumSRSSymbols(self) -> Literal[1, 2, 4, 8, 10, 12, 14]:
        return self._NumSRSSymbols

    @NumSRSSymbols.setter
    def NumSRSSymbols(self, value: Literal[1, 2, 4, 8, 10, 12, 14]) -> None:
        assert value in (1, 2, 4, 8, 10, 12, 14), "The value must be 1, 2, 4, 8, 10, 12, or 14"
        self._NumSRSSymbols = value

    @property
    def CSRS(self) -> int:
        return self._CSRS

    @CSRS.setter
    def CSRS(self, value: int) -> None:
        assert 0 <= value <= 63, "The value must be 0..63"
        self._CSRS = value

    @property
    def BSRS(self) -> Literal[0, 1, 2, 3]:
        return self._BSRS

    @BSRS.setter
    def BSRS(self, value: Literal[0, 1, 2, 3]) -> None:
        assert value in (0, 1, 2, 3), "The value must be 0, 1, 2, or 3"
        self._BSRS = value

    @property
    def BHop(self) -> Literal[0, 1, 2, 3]:
        return self._BHop

    @BHop.setter
    def BHop(self, value: Literal[0, 1, 2, 3]) -> None:
        assert value in (0, 1, 2, 3), "The value must be 0, 1, 2, or 3"
        self._BHop = value

    @property
    def KTC(self) -> Literal[2, 4, 8]:
        return self._KTC

    @KTC.setter
    def KTC(self, value: Literal[2, 4, 8]) -> None:
        assert value in (2, 4, 8), "The value must be 2, 4, or 8"
        self._KTC = value

    @property
    def KBarTC(self) -> int:
        return self._KBarTC

    @KBarTC.setter
    def KBarTC(self, value: int) -> None:
        assert 0 <= value <= 7, "The value must be 0..7"
        self._KBarTC = value

    @property
    def CyclicShift(self) -> int:
        return self._CyclicShift

    @CyclicShift.setter
    def CyclicShift(self, value: int) -> None:
        assert 0 <= value <= 11, "The value must be 0..11"
        self._CyclicShift = value

    @property
    def NSRSID(self) -> int:
        return self._NSRSID

    @NSRSID.setter
    def NSRSID(self, value: int) -> None:
        assert 0 <= value <= 65535, "The value must be 0..65535"
        self._NSRSID = value

    @property
    def FrequencyStart(self) -> int:
        return self._FrequencyStart

    @FrequencyStart.setter
    def FrequencyStart(self, value: int) -> None:
        assert 0 <= value <= 271, "The value must be 0..271"
        self._FrequencyStart = value

    @property
    def NRRC(self) -> int:
        return self._NRRC

    @NRRC.setter
    def NRRC(self, value: int) -> None:
        assert 0 <= value <= 67, "The value must be 0..67"
        self._NRRC = value

    @property
    def SRSPeriod(self) -> Literal["on", "off"] | list[int]:
        return self._SRSPeriod

    @SRSPeriod.setter
    def SRSPeriod(self, value: Literal["on", "off"] | list[int]) -> None:
        if isinstance(value, str):
            assert value in ("on", "off"), "The value must be 'on', 'off', or [Tsrs, Toffset]"
        else:
            assert len(value) == 2, "The value must be 'on', 'off', or [Tsrs, Toffset]"
            assert 0 <= value[1] < value[0], "Toffset must be in the range 0..Tsrs-1"
        self._SRSPeriod = value

    @property
    def GroupSeqHopping(self) -> Literal["neither", "groupHopping", "sequenceHopping"]:
        return self._GroupSeqHopping

    @GroupSeqHopping.setter
    def GroupSeqHopping(self, value: Literal["neither", "groupHopping", "sequenceHopping"]) -> None:
        assert value in (
            "neither",
            "groupHopping",
            "sequenceHopping",
        ), "The value must be 'neither', 'groupHopping', or 'sequenceHopping'"
        self._GroupSeqHopping = value

    @property
    def ResourceType(self) -> Literal["periodic", "semi-persistent", "aperiodic"]:
        return self._ResourceType

    @ResourceType.setter
    def ResourceType(self, value: Literal["periodic", "semi-persistent", "aperiodic"]) -> None:
        assert value in (
            "periodic",
            "semi-persistent",
            "aperiodic",
        ), "The value must be 'periodic', 'semi-persistent', or 'aperiodic'"
        self._ResourceType = value

    @property
    def EnableEightPortTDM(self) -> bool:
        return self._EnableEightPortTDM

    @EnableEightPortTDM.setter
    def EnableEightPortTDM(self, value: bool) -> None:
        self._EnableEightPortTDM = value

    @property
    def CombOffsetHopping(self) -> bool:
        return self._CombOffsetHopping

    @CombOffsetHopping.setter
    def CombOffsetHopping(self, value: bool) -> None:
        self._CombOffsetHopping = value

    @property
    def CyclicShiftHopping(self) -> bool:
        return self._CyclicShiftHopping

    @CyclicShiftHopping.setter
    def CyclicShiftHopping(self, value: bool) -> None:
        self._CyclicShiftHopping = value

    @property
    def SRSPositioning(self) -> bool:
        return self._SRSPositioning

    @SRSPositioning.setter
    def SRSPositioning(self, value: bool) -> None:
        self._SRSPositioning = value

    @property
    def FrequencyScalingFactor(self) -> Literal[1, 2, 4]:
        return self._FrequencyScalingFactor

    @FrequencyScalingFactor.setter
    def FrequencyScalingFactor(self, value: Literal[1, 2, 4]) -> None:
        assert value in (1, 2, 4), "The value must be 1, 2, or 4"
        self._FrequencyScalingFactor = value


def _assertSupported(srs: nrSRSConfig) -> None:
    if srs.BHop < srs.BSRS:
        raise NotImplementedError("frequency hopping (BHop < BSRS) is not yet implemented")
    if srs.GroupSeqHopping != "neither":
        raise NotImplementedError("GroupSeqHopping other than 'neither' is not yet implemented")
    if srs.EnableEightPortTDM:
        raise NotImplementedError("EnableEightPortTDM is not yet implemented")
    if srs.CombOffsetHopping:
        raise NotImplementedError("CombOffsetHopping is not yet implemented")
    if srs.CyclicShiftHopping:
        raise NotImplementedError("CyclicShiftHopping is not yet implemented")
    if srs.SRSPositioning:
        raise NotImplementedError("SRSPositioning is not yet implemented")
    if srs.FrequencyScalingFactor != 1:
        raise NotImplementedError("FrequencyScalingFactor > 1 (partial frequency sounding) is not yet implemented")


def _periodicityAndOffset(srsPeriod: Literal["on", "off"] | list[int]) -> tuple[int, int]:
    if srsPeriod == "on":
        return 1, 0
    if srsPeriod == "off":
        return 0, 0
    Tsrs, Toff = srsPeriod
    return int(Tsrs), int(Toff)


def _relativeNSlotAndSFN(nslot: int, nframe: int, slotsPerFrame: int) -> tuple[int, int]:
    nframe = nframe + nslot // slotsPerFrame
    return nslot % slotsPerFrame, nframe % 1024


def _isCandidateSlot(carrier: nrCarrierConfig, srs: nrSRSConfig) -> bool:
    """TS 38.211 Section 6.4.1.4.4 (simplified: no hyperframe/positioning branch)."""
    Tsrs, Toff = _periodicityAndOffset(srs.SRSPeriod)
    if Tsrs == 0:
        return False
    nslot, nframe = _relativeNSlotAndSFN(carrier.NSlot, carrier.NFrame, carrier.SlotsPerFrame)
    return (carrier.SlotsPerFrame * nframe + nslot - Toff) % Tsrs == 0


def _portCyclicShifts(srs: nrSRSConfig) -> NDArray[np.floating]:
    """Cyclic shift alpha per port (TS 38.211 6.4.1.4.2), simplified: no 8-port TDM, no
    cyclic-shift hopping (so alpha is constant across OFDM symbols)."""
    NPorts = srs.NumSRSPorts
    nCSmax = _NCS_MAX[srs.KTC]

    pBar = 1000 + np.arange(NPorts)
    if NPorts == 8 and nCSmax == 6:
        scaling = 4
    elif (NPorts == 4 and nCSmax == 6) or (NPorts == 8 and nCSmax == 12):
        scaling = 2
    else:
        scaling = 1

    nCSp = (srs.CyclicShift + nCSmax * np.floor((pBar - 1000) / scaling) / (NPorts / scaling)) % nCSmax
    return (2 * np.pi / nCSmax) * nCSp


def _frequencyPositionOffset(srs: nrSRSConfig) -> NDArray[np.int_]:
    """k0bar per port (TS 38.211 6.4.1.4.3), simplified: no comb-offset hopping, no SRS
    positioning."""
    NPorts = srs.NumSRSPorts
    KTC = srs.KTC
    nCSmax = _NCS_MAX[KTC]

    pBar = np.arange(NPorts)
    freqShiftPort = np.zeros(NPorts, dtype=int)
    if NPorts == 4 and (nCSmax == 6 or (nCSmax in (8, 12) and srs.CyclicShift >= nCSmax / 2)):
        freqShiftPort = 2 * (pBar % 2)
    elif NPorts == 8:
        if nCSmax == 6:
            freqShiftPort = pBar % 4
        elif nCSmax == 12 or (nCSmax == 8 and srs.CyclicShift >= nCSmax / 2):
            freqShiftPort = 2 * (pBar % 2)

    kTC = (srs.KBarTC + freqShiftPort * KTC / 4) % KTC
    return (srs.FrequencyStart * 12 + kTC).astype(int)


def _frequencyPositionIndex(srs: nrSRSConfig) -> tuple[int, int]:
    """Frequency hopping offset nFH in subcarriers (TS 38.211 6.4.1.4.3), simplified: no
    frequency hopping (BHop >= BSRS is enforced by _assertSupported, so the n_b adjustment
    via F_b never applies)."""
    b = range(srs.BSRS + 1)
    mSRSb = np.array([_srsBandwidthConfig(srs.CSRS, bb)[0] for bb in b])
    Nb = np.array([_srsBandwidthConfig(srs.CSRS, bb)[1] for bb in b])

    nb = np.floor(4 * srs.NRRC / mSRSb).astype(int) % Nb
    nFH = int(12 * np.sum(mSRSb * nb))
    mSRS_BSRS = int(mSRSb[-1])
    return nFH, mSRS_BSRS


def nrSRS(carrier: nrCarrierConfig, srs: nrSRSConfig) -> tuple[NDArray[np.complex128], dict]:
    """Generate uplink sounding reference signal (SRS) symbols."""
    _assertSupported(srs)

    if not _isCandidateSlot(carrier, srs):
        return np.zeros(0, dtype=np.complex128), {"SeqGroup": None, "NSeq": None, "Alpha": None, "SeqLength": 0}

    NSym = srs.NumSRSSymbols
    u = srs.NSRSID % 30
    v = 0
    alpha = _portCyclicShifts(srs)
    nFH, mSRS_BSRS = _frequencyPositionIndex(srs)
    Msc = mSRS_BSRS * 12 // srs.KTC

    baseSeq = nrLowPAPRS(u, v, alpha, Msc)  # shape (Msc, NumSRSPorts)
    sym = np.tile(baseSeq, (NSym, 1))  # (Msc*NSym, NumSRSPorts), symbol-major per port

    info = {"SeqGroup": u, "NSeq": v, "Alpha": alpha, "SeqLength": Msc}
    return sym.ravel(order="F"), info


def nrSRSIndices(carrier: nrCarrierConfig, srs: nrSRSConfig) -> NDArray[np.int_]:
    """Generate uplink SRS resource element indices."""
    _assertSupported(srs)

    if not _isCandidateSlot(carrier, srs):
        return np.array([], dtype=int)

    NPorts = srs.NumSRSPorts
    NSym = srs.NumSRSSymbols
    KTC = srs.KTC

    k0bar = _frequencyPositionOffset(srs)
    nFH, mSRS_BSRS = _frequencyPositionIndex(srs)
    k0 = k0bar + nFH  # per port
    Msc = mSRS_BSRS * 12 // KTC

    totalSC = carrier.NSizeGrid * 12
    totalSyms = carrier.SymbolsPerSlot
    portStride = totalSC * totalSyms

    l = srs.SymbolStart + np.arange(NSym)
    k = np.arange(Msc) * KTC

    indices = []
    for port in range(NPorts):
        base = k0[port] + k
        portIndices = (base[:, None] + l[None, :] * totalSC).ravel(order="F")
        indices.append(portIndices + port * portStride)
    return np.concatenate(indices)
