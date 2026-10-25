# Ref: TS 38.211 Section 6.3.3
from __future__ import annotations

import csv
from typing import Literal

import numpy as np
from importlib_resources import as_file, files
from numpy.typing import NDArray

from py3gpp import codes
from py3gpp.dl.ofdm import nrCarrierConfig

LRA = 839


def _zadoffChuSeq(u: int, n: int) -> NDArray[np.complex128]:
    """Bare Zadoff-Chu sequence (TS 38.211 5.2.2 base formula). PRACH uses this directly
    (matching MATLAB's own `zadoffChuSeq`), not the generic `nrLowPAPRS` (which decomposes a
    sequence via group/sequence numbers (u,v) and is used by SRS/PUCCH/PUSCH DM-RS instead)."""
    m = np.arange(n)
    return np.exp(-1j * np.pi * u * m * (m + 1) / n)


# TS 38.211 Table 6.3.3.1-1 (long preambles, L_RA=839). PRACHDuration is N_u / N_u(format 0),
# i.e. how many "format 0 units" the preamble sequence spans (confirmed against a live
# nrPRACHConfig: PRACHDuration = 1, 2, 4, 1 for formats 0, 1, 2, 3 respectively). "W" is TS
# 38.101-1 Table F.5.5-1's windowing parameter, combined with N_CP in nrPRACHOFDMInfo via
# E = floor((N_CP - W) * nfft / nfft_nominal).
_LONG_FORMAT_PARAMS: dict[str, dict[str, float]] = {
    "0": {"SubcarrierSpacing": 1.25, "N_u": 24576, "N_CP": 3168, "PRACHDuration": 1, "W": 2307},
    "1": {"SubcarrierSpacing": 1.25, "N_u": 49152, "N_CP": 21024, "PRACHDuration": 2, "W": 20163},
    "2": {"SubcarrierSpacing": 1.25, "N_u": 98304, "N_CP": 4688, "PRACHDuration": 4, "W": 3827},
    "3": {"SubcarrierSpacing": 5, "N_u": 24576, "N_CP": 3168, "PRACHDuration": 1, "W": 2952},
}

# TS 38.211 Table 6.3.3.1-5 (Ncs, unrestricted set, formats 0-2) and 6.3.3.1-6 (format 3),
# indexed by ZeroCorrelationZone (0-15).
_NCS_UNRESTRICTED_012 = [0, 13, 15, 18, 22, 26, 32, 38, 46, 59, 76, 93, 119, 167, 279, 419]
_NCS_UNRESTRICTED_3 = [0, 13, 26, 33, 38, 41, 49, 55, 64, 76, 93, 119, 139, 209, 279, 419]

# TS 38.211 Table 6.3.3.2-1 (L_RA=839 PRACH/PUSCH subcarrier-spacing combinations):
# (PRACH SCS, PUSCH SCS) -> (NRBAllocation, kbar).
_SCS_COMBINATIONS_839: dict[tuple[float, int], tuple[int, int]] = {
    (1.25, 15): (6, 7),
    (1.25, 30): (3, 1),
    (1.25, 60): (2, 133),
    (5, 15): (24, 12),
    (5, 30): (12, 10),
    (5, 60): (6, 7),
}

_DUPLEX_GROUP: dict[str, str] = {"FDD": "PairedSUL", "SUL": "PairedSUL", "TDD": "Unpaired"}


def _load_root_table() -> NDArray[np.int_]:
    source = files(codes).joinpath("prach_root_839.csv")
    with as_file(source) as path:
        return np.loadtxt(path, dtype=int)


def _load_config_table() -> tuple[dict[tuple[str, int], list[tuple[int, int, int, int]]], dict[tuple[str, int], str]]:
    rows: dict[tuple[str, int], list[tuple[int, int, int, int]]] = {}
    formats: dict[tuple[str, int], str] = {}
    source = files(codes).joinpath("prach_config_fr1.csv")
    with as_file(source) as path, open(path, newline="") as f:
        for row in csv.DictReader(f):
            key = (row["DuplexGroup"], int(row["ConfigurationIndex"]))
            rows.setdefault(key, []).append(
                (int(row["x"]), int(row["y"]), int(row["SubframeNumber"]), int(row["StartingSymbol"]))
            )
            formats[key] = row["Format"]
    return rows, formats


_ROOT_TABLE_839 = _load_root_table()
_CONFIG_ROWS, _CONFIG_FORMAT = _load_config_table()


class nrPRACHConfig:
    """PRACH configuration parameters."""

    def __init__(self) -> None:
        self._FrequencyRange: Literal["FR1"] = "FR1"
        self._DuplexMode: Literal["FDD", "TDD", "SUL"] = "FDD"
        self._ConfigurationIndex: int = 0
        self._SequenceIndex: int = 0
        self._PreambleIndex: int = 0
        self._RestrictedSet: Literal["UnrestrictedSet", "RestrictedSetTypeA", "RestrictedSetTypeB"] = "UnrestrictedSet"
        self._ZeroCorrelationZone: int = 0
        self._NPRACHSlot: int = 0
        self._RBOffset: int = 0
        self._FrequencyStart: int = 0
        self._FrequencyIndex: int = 0
        self._assertValidConfigurationIndex(self._DuplexMode, self._ConfigurationIndex)

    def _assertValidConfigurationIndex(self, duplexMode: str, configurationIndex: int) -> None:
        key = (_DUPLEX_GROUP[duplexMode], configurationIndex)
        assert key in _CONFIG_ROWS, (
            f"ConfigurationIndex={configurationIndex} has no long-preamble (Format 0-3) "
            f"configuration for DuplexMode={duplexMode}"
        )

    @property
    def FrequencyRange(self) -> Literal["FR1"]:
        return self._FrequencyRange

    @FrequencyRange.setter
    def FrequencyRange(self, value: Literal["FR1"]) -> None:
        assert value == "FR1", "FR2 is not yet implemented (FR2 has no long-preamble configurations)"
        self._FrequencyRange = value

    @property
    def DuplexMode(self) -> Literal["FDD", "TDD", "SUL"]:
        return self._DuplexMode

    @DuplexMode.setter
    def DuplexMode(self, value: Literal["FDD", "TDD", "SUL"]) -> None:
        assert value in ("FDD", "TDD", "SUL"), "The value must be 'FDD', 'TDD', or 'SUL'"
        self._assertValidConfigurationIndex(value, self._ConfigurationIndex)
        self._DuplexMode = value

    @property
    def ConfigurationIndex(self) -> int:
        return self._ConfigurationIndex

    @ConfigurationIndex.setter
    def ConfigurationIndex(self, value: int) -> None:
        self._assertValidConfigurationIndex(self._DuplexMode, value)
        self._ConfigurationIndex = value

    @property
    def SequenceIndex(self) -> int:
        return self._SequenceIndex

    @SequenceIndex.setter
    def SequenceIndex(self, value: int) -> None:
        assert 0 <= value <= 837, "The value must be 0..837"
        self._SequenceIndex = value

    @property
    def PreambleIndex(self) -> int:
        return self._PreambleIndex

    @PreambleIndex.setter
    def PreambleIndex(self, value: int) -> None:
        assert 0 <= value <= 63, "The value must be 0..63"
        self._PreambleIndex = value

    @property
    def RestrictedSet(self) -> Literal["UnrestrictedSet", "RestrictedSetTypeA", "RestrictedSetTypeB"]:
        return self._RestrictedSet

    @RestrictedSet.setter
    def RestrictedSet(self, value: Literal["UnrestrictedSet", "RestrictedSetTypeA", "RestrictedSetTypeB"]) -> None:
        assert value in (
            "UnrestrictedSet",
            "RestrictedSetTypeA",
            "RestrictedSetTypeB",
        ), "The value must be 'UnrestrictedSet', 'RestrictedSetTypeA', or 'RestrictedSetTypeB'"
        self._RestrictedSet = value

    @property
    def ZeroCorrelationZone(self) -> int:
        return self._ZeroCorrelationZone

    @ZeroCorrelationZone.setter
    def ZeroCorrelationZone(self, value: int) -> None:
        assert 0 <= value <= 15, "The value must be 0..15"
        self._ZeroCorrelationZone = value

    @property
    def NPRACHSlot(self) -> int:
        return self._NPRACHSlot

    @NPRACHSlot.setter
    def NPRACHSlot(self, value: int) -> None:
        assert value >= 0, "The value must be >= 0"
        self._NPRACHSlot = value

    @property
    def RBOffset(self) -> int:
        return self._RBOffset

    @RBOffset.setter
    def RBOffset(self, value: int) -> None:
        assert value >= 0, "The value must be >= 0"
        self._RBOffset = value

    @property
    def FrequencyStart(self) -> int:
        return self._FrequencyStart

    @FrequencyStart.setter
    def FrequencyStart(self, value: int) -> None:
        assert value >= 0, "The value must be >= 0"
        self._FrequencyStart = value

    @property
    def FrequencyIndex(self) -> int:
        return self._FrequencyIndex

    @FrequencyIndex.setter
    def FrequencyIndex(self, value: int) -> None:
        assert value >= 0, "The value must be >= 0"
        self._FrequencyIndex = value

    @property
    def LRA(self) -> int:
        return LRA

    @property
    def _configRows(self) -> list[tuple[int, int, int, int]]:
        return _CONFIG_ROWS[(_DUPLEX_GROUP[self.DuplexMode], self.ConfigurationIndex)]

    @property
    def Format(self) -> Literal["0", "1", "2", "3"]:
        return _CONFIG_FORMAT[(_DUPLEX_GROUP[self.DuplexMode], self.ConfigurationIndex)]  # type: ignore[return-value]

    @property
    def SubcarrierSpacing(self) -> float:
        return _LONG_FORMAT_PARAMS[self.Format]["SubcarrierSpacing"]

    @property
    def PRACHDuration(self) -> int:
        return int(_LONG_FORMAT_PARAMS[self.Format]["PRACHDuration"])

    @property
    def StartingSymbol(self) -> int:
        return self._configRows[0][3]


def _getNcs(prach: nrPRACHConfig) -> int:
    if prach.RestrictedSet != "UnrestrictedSet":
        raise NotImplementedError("RestrictedSetTypeA/B is not yet implemented")
    table = _NCS_UNRESTRICTED_3 if prach.Format == "3" else _NCS_UNRESTRICTED_012
    return table[prach.ZeroCorrelationZone]


def _isActive(prach: nrPRACHConfig) -> bool:
    """TS 38.211 Section 6.3.3.2, long-preamble-only path (skips the short-preamble
    ActivePRACHSlot check, which only applies to PRACH subcarrier spacings of 30/120/480/960 kHz)."""
    if prach.Format == "3":
        raise NotImplementedError("Format 3 (5 kHz) is not yet implemented")

    L = prach.PRACHDuration
    if prach.Format == "1":
        L += 1
    nSlot = prach.NPRACHSlot * L + np.arange(L)
    nslot = nSlot % 10
    sfn = nSlot // 10

    rows = prach._configRows
    x = rows[0][0]
    validSF = {r[2] for r in rows}
    validY = {r[1] for r in rows}
    return any(int(n) in validSF and int(s) % x in validY for n, s in zip(nslot, sfn))


def _getPreambleSeqParameters(prach: nrPRACHConfig) -> tuple[int, int, int]:
    """Unrestricted-set-only port of TS 38.211 Section 6.3.3.1's root/cyclic-shift derivation.

    Each root sequence provides floor(LRA/Ncs) distinct cyclic shifts (or exactly 1, with no
    shift, when Ncs=0); PreambleIndex walks through shifts of the current root before moving to
    the next logical root index.
    """
    if prach.RestrictedSet != "UnrestrictedSet":
        raise NotImplementedError("RestrictedSetTypeA/B is not yet implemented")

    Ncs = _getNcs(prach)
    if Ncs == 0:
        shiftsPerRoot = 1
        v = 0
        rootOffset = prach.PreambleIndex
    else:
        shiftsPerRoot = LRA // Ncs
        v = prach.PreambleIndex % shiftsPerRoot
        rootOffset = prach.PreambleIndex // shiftsPerRoot

    seqIdx = (prach.SequenceIndex + rootOffset) % (LRA - 1)
    u = int(_ROOT_TABLE_839[seqIdx])
    C_v = v * Ncs
    return u, C_v, Ncs


def nrPRACH(carrier: nrCarrierConfig, prach: nrPRACHConfig) -> tuple[NDArray[np.complex128], dict]:
    """Generate PRACH symbols."""
    if not _isActive(prach):
        return np.array([], dtype=np.complex128), {"RootSequence": None, "CyclicShift": None, "NumCyclicShifts": 0}

    u, C_v, numCyclicShifts = _getPreambleSeqParameters(prach)
    info = {"RootSequence": u, "CyclicShift": C_v, "NumCyclicShifts": numCyclicShifts}

    x_u = _zadoffChuSeq(u, LRA)
    x_uv = np.roll(x_u, -C_v)
    y_uv = np.fft.fft(x_uv)

    L = prach.PRACHDuration
    sym = np.tile(y_uv, L)
    return sym, info


def nrPRACHIndices(carrier: nrCarrierConfig, prach: nrPRACHConfig) -> NDArray[np.int_]:
    """Generate PRACH resource element indices."""
    if not _isActive(prach):
        return np.array([], dtype=int)
    if prach.Format == "3":
        raise NotImplementedError("Format 3 (5 kHz) is not yet implemented")

    carrierNRB = carrier.NSizeGrid
    carrierSCS = carrier.SubcarrierSpacing
    prachSCS = prach.SubcarrierSpacing

    NRBAllocation, kbar = _SCS_COMBINATIONS_839[(prachSCS, carrierSCS)]
    K = carrierSCS / prachSCS

    rbSetOffset = prach.FrequencyIndex * NRBAllocation
    PRBFirst = prach.RBOffset + prach.FrequencyStart + rbSetOffset
    assert PRBFirst + NRBAllocation <= carrierNRB, "PRACH allocation exceeds the carrier grid"

    k0 = 0
    k1 = k0 + (PRBFirst - carrierNRB / 2) * 12

    # PRACH occupies its own grid, at its own (finer) numerology: K times as many
    # subcarriers as the carrier's own grid, confirmed against the live
    # nr5g.internal.prach.gridSize helper (gridSize(52, 15, <Format 0 config>, 1) == [7488, 1]
    # == K * carrierNRB * 12 for K=12).
    totalSC = int(K * carrierNRB * 12)
    zeroFreq = totalSC / 2
    first = K * k1 + kbar
    k = np.ceil(np.arange(LRA) + zeroFreq + first).astype(int)

    L = prach.PRACHDuration
    l = prach.StartingSymbol + np.arange(L)

    indices = (k[:, None] + l[None, :] * totalSC).ravel(order="F")
    return indices


def nrPRACHOFDMInfo(carrier: nrCarrierConfig, prach: nrPRACHConfig) -> dict:
    """Get PRACH OFDM information."""
    if prach.Format != "0":
        raise NotImplementedError("Only Format 0 is verified for nrPRACHOFDMInfo so far")
    if prach.StartingSymbol != 0:
        raise NotImplementedError("StartingSymbol > 0 (subframe-straddling occasions) is not yet implemented")

    sr_nominal = 30.72e6
    params = _LONG_FORMAT_PARAMS[prach.Format]
    n_idft_nominal = 24576  # TS 38.211 6.3.3.2: nominal IDFT size for formats 0-2 (mu=0)

    # Carrier's own OFDM sample rate, at the carrier's own numerology (reuses the same
    # Nfft-selection rule as nrOFDMInfo: smallest power of 2 with >=85% occupancy).
    carrierNfft = 2 ** int(np.ceil(np.log2(carrier.NSizeGrid * 12 / 0.85)))
    carrierSampleRate = carrierNfft * carrier.SubcarrierSpacing * 1000

    R = carrierSampleRate / sr_nominal
    nfft = int(round(n_idft_nominal * R))
    cpLength = int(round(params["N_CP"] * R))

    samplesPerSubframe = carrierSampleRate * 1e-3  # 1 subframe = 1ms; SubframesPerPRACHSlot=1 for Format 0
    guardLength = int(round(samplesPerSubframe)) - cpLength - nfft
    assert guardLength >= 0, "computed guard length is negative; unsupported configuration"

    windowing = int(np.floor((params["N_CP"] - params["W"]) * R))

    return {
        "Nfft": nfft,
        "SampleRate": carrierSampleRate,
        "CyclicPrefixLengths": cpLength,
        "GuardLengths": guardLength,
        "SymbolLengths": cpLength + nfft + guardLength,
        "OffsetLength": 0,
        "Windowing": windowing,
    }
