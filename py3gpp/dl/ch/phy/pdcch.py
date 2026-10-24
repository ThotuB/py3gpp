# Ref: TS 38.211 Section 7.3.2
from __future__ import annotations

from typing import Literal, Sequence

import numpy as np
from numpy.typing import NDArray

from py3gpp.dl.ofdm import nrCarrierConfig
from py3gpp.plc.sym import nrPRBS, nrSymbolDemodulate, nrSymbolModulate


class nrCORESETConfig:
    """Control resource set (CORESET) configuration parameters."""

    def __init__(self) -> None:
        self._ControlResourceSetId: int = 0
        self._FrequencyResources: list[int] = [1] + [0] * 44
        self._Duration: Literal[1, 2, 3] = 1
        self._CCEREGMapping: Literal["interleaved", "noninterleaved"] = "noninterleaved"
        self._REGBundleSize: Literal[2, 3, 6] = 6
        self._InterleaverSize: Literal[2, 3, 6] = 2
        self._ShiftIndex: int | None = None

    @property
    def ControlResourceSetId(self) -> int:
        return self._ControlResourceSetId

    @ControlResourceSetId.setter
    def ControlResourceSetId(self, value: int) -> None:
        assert 0 <= value <= 11, "The value must be 0..11"
        self._ControlResourceSetId = value

    @property
    def FrequencyResources(self) -> list[int]:
        return self._FrequencyResources

    @FrequencyResources.setter
    def FrequencyResources(self, value: list[int]) -> None:
        assert len(value) == 45, "FrequencyResources must have 45 elements"
        assert all(v in (0, 1) for v in value), "FrequencyResources elements must be 0 or 1"
        self._FrequencyResources = value

    @property
    def Duration(self) -> Literal[1, 2, 3]:
        return self._Duration

    @Duration.setter
    def Duration(self, value: Literal[1, 2, 3]) -> None:
        assert value in (1, 2, 3), "The value must be 1, 2, or 3"
        self._Duration = value

    @property
    def CCEREGMapping(self) -> Literal["interleaved", "noninterleaved"]:
        return self._CCEREGMapping

    @CCEREGMapping.setter
    def CCEREGMapping(self, value: Literal["interleaved", "noninterleaved"]) -> None:
        assert value in ("interleaved", "noninterleaved"), "The value must be 'interleaved' or 'noninterleaved'"
        self._CCEREGMapping = value

    @property
    def REGBundleSize(self) -> Literal[2, 3, 6]:
        return self._REGBundleSize

    @REGBundleSize.setter
    def REGBundleSize(self, value: Literal[2, 3, 6]) -> None:
        assert value in (2, 3, 6), "The value must be 2, 3, or 6"
        self._REGBundleSize = value

    @property
    def InterleaverSize(self) -> Literal[2, 3, 6]:
        return self._InterleaverSize

    @InterleaverSize.setter
    def InterleaverSize(self, value: Literal[2, 3, 6]) -> None:
        assert value in (2, 3, 6), "The value must be 2, 3, or 6"
        self._InterleaverSize = value

    @property
    def ShiftIndex(self) -> int | None:
        return self._ShiftIndex

    @ShiftIndex.setter
    def ShiftIndex(self, value: int) -> None:
        assert 0 <= value <= 274, "The value must be 0..274"
        self._ShiftIndex = value

    @property
    def PRBSet(self) -> list[int]:
        """Resolve FrequencyResources into the absolute list of PRB indices (6-RB granularity)."""
        prbs: list[int] = []
        for group, bit in enumerate(self._FrequencyResources):
            if bit:
                prbs.extend(range(group * 6, group * 6 + 6))
        return prbs


class nrSearchSpaceConfig:
    """Search space set configuration parameters."""

    def __init__(self) -> None:
        self._SearchSpaceId: int = 0
        self._ControlResourceSetId: int = 0
        self._SearchSpaceType: Literal["common", "ue-specific"] = "common"
        self._NumCandidates: dict[int, int] = {1: 0, 2: 0, 4: 0, 8: 0, 16: 0}

    @property
    def SearchSpaceId(self) -> int:
        return self._SearchSpaceId

    @SearchSpaceId.setter
    def SearchSpaceId(self, value: int) -> None:
        assert 0 <= value <= 39, "The value must be 0..39"
        self._SearchSpaceId = value

    @property
    def ControlResourceSetId(self) -> int:
        return self._ControlResourceSetId

    @ControlResourceSetId.setter
    def ControlResourceSetId(self, value: int) -> None:
        assert 0 <= value <= 11, "The value must be 0..11"
        self._ControlResourceSetId = value

    @property
    def SearchSpaceType(self) -> Literal["common", "ue-specific"]:
        return self._SearchSpaceType

    @SearchSpaceType.setter
    def SearchSpaceType(self, value: Literal["common", "ue-specific"]) -> None:
        assert value in ("common", "ue-specific"), "The value must be 'common' or 'ue-specific'"
        self._SearchSpaceType = value

    @property
    def NumCandidates(self) -> dict[int, int]:
        return self._NumCandidates

    @NumCandidates.setter
    def NumCandidates(self, value: dict[int, int]) -> None:
        assert set(value.keys()) <= {1, 2, 4, 8, 16}, "Keys must be aggregation levels in {1, 2, 4, 8, 16}"
        assert all(v in (0, 1, 2, 3, 4, 5, 6, 8) for v in value.values()), "Values must be in {0,1,2,3,4,5,6,8}"
        self._NumCandidates = value


class nrPDCCHConfig:
    """PDCCH configuration parameters."""

    def __init__(self) -> None:
        self.CORESET: nrCORESETConfig = nrCORESETConfig()
        self.SearchSpace: nrSearchSpaceConfig = nrSearchSpaceConfig()
        self._RNTI: int = 0

    @property
    def RNTI(self) -> int:
        return self._RNTI

    @RNTI.setter
    def RNTI(self, value: int) -> None:
        assert 0 <= value <= 65535, "The value must be 0..65535"
        self._RNTI = value


def nrPDCCHPRBS(rnti: int, nid: int, length: int) -> NDArray[np.int32]:
    """Generate PDCCH scrambling sequence."""
    cinit = (rnti * 2**16 + nid) % 2**31
    return nrPRBS(cinit, length)


def nrPDCCH(bits: NDArray[np.int_], rnti: int, nid: int) -> NDArray[np.complex128]:
    """Generate PDCCH modulation symbols."""
    scrambling_seq = nrPDCCHPRBS(rnti, nid, len(bits))
    scrambled = np.bitwise_xor(bits, scrambling_seq)
    return nrSymbolModulate(scrambled, "QPSK")


def nrPDCCHDecode(sym: NDArray[np.complex128], rnti: int, nid: int) -> NDArray[np.float64]:
    """Decode PDCCH modulation symbols."""
    demod = nrSymbolDemodulate(sym, "QPSK")
    scrambling_seq = nrPDCCHPRBS(rnti, nid, len(demod))
    return np.multiply(demod, (-scrambling_seq * 2 + 1))


def nrPDCCHResources(
    carrier: nrCarrierConfig, coreset: nrCORESETConfig, cce_indices: Sequence[int]
) -> tuple[NDArray[np.int_], NDArray[np.int_]]:
    """Generate PDCCH and PDCCH DM-RS resources."""
    if coreset.CCEREGMapping == "interleaved":
        raise NotImplementedError("interleaved CCE-to-REG mapping is not yet implemented")

    # TS 38.211 7.3.2.2: REGs are numbered time-first within the CORESET's allocated PRBs;
    # for a non-interleaved mapping, CCE c consists of REGs {6c, ..., 6c+5} directly.
    prb_set = coreset.PRBSet
    D = coreset.Duration
    n_reg = len(prb_set) * D
    total_subcarriers = 12 * carrier.NSizeGrid

    # TS 38.211 7.4.1.3.2: PDCCH DM-RS occupies subcarriers {1, 5, 9} within each PRB/symbol.
    dmrs_local = (1, 5, 9)
    data_local = tuple(k for k in range(12) if k not in dmrs_local)

    pdcch_re: list[int] = []
    dmrs_re: list[int] = []
    for cce in cce_indices:
        reg_start = 6 * cce
        for reg in range(reg_start, reg_start + 6):
            assert 0 <= reg < n_reg, f"REG index {reg} (from CCE {cce}) is out of range for this CORESET"
            prb = prb_set[reg // D]
            symbol = reg % D
            base = prb * 12 + symbol * total_subcarriers
            pdcch_re.extend(base + k for k in data_local)
            dmrs_re.extend(base + k for k in dmrs_local)

    return np.array(pdcch_re, dtype=int), np.array(dmrs_re, dtype=int)
