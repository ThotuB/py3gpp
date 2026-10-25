# 38.211
from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import numpy as np
from numpy.typing import NDArray

from py3gpp.dl.ofdm import nrCarrierConfig
from py3gpp.plc.sym import nrPRBS, nrSymbolModulate
from py3gpp.ul.sig.pusch_dmrs import PUSCHDMRScinit, PUSCHDMRSSyms

if TYPE_CHECKING:
    from py3gpp.ul.ch.phy.pusch import nrPUSCHConfig


class nrPUSCHPTRSConfig:
    """PUSCH PT-RS configuration parameters (CP-OFDM/non-transform-precoded only)."""

    def __init__(self) -> None:
        self._TimeDensity: Literal[1, 2, 4] = 1
        self._FrequencyDensity: Literal[2, 4] = 2
        self._REOffset: Literal["00", "01", "10", "11"] = "00"
        self._PTRSPortSet: list[int] = []

    @property
    def TimeDensity(self) -> Literal[1, 2, 4]:
        return self._TimeDensity

    @TimeDensity.setter
    def TimeDensity(self, value: Literal[1, 2, 4]) -> None:
        assert value in (1, 2, 4), "The value must be one of 1,2,4"
        self._TimeDensity = value

    @property
    def FrequencyDensity(self) -> Literal[2, 4]:
        return self._FrequencyDensity

    @FrequencyDensity.setter
    def FrequencyDensity(self, value: Literal[2, 4]) -> None:
        assert value in (2, 4), "The value must be one of 2,4"
        self._FrequencyDensity = value

    @property
    def REOffset(self) -> Literal["00", "01", "10", "11"]:
        return self._REOffset

    @REOffset.setter
    def REOffset(self, value: Literal["00", "01", "10", "11"]) -> None:
        assert value in ("00", "01", "10", "11"), "The value must be one of '00','01','10','11'"
        self._REOffset = value

    @property
    def PTRSPortSet(self) -> list[int]:
        return self._PTRSPortSet

    @PTRSPortSet.setter
    def PTRSPortSet(self, value: list[int]) -> None:
        self._PTRSPortSet = value


def _ptrsPRBSet(cfg: nrPUSCHConfig) -> NDArray[np.int_]:
    """TS 38.211 7.4.1.2.2: PT-RS subcarrier offset within the DM-RS base sequence (DMRSConfigurationType=1)."""
    dmrsRefTable = np.array([0, 2, 6, 8])
    kREIdx = int(cfg.PTRS.REOffset, 2)
    dmrsRef = dmrsRefTable[kREIdx]

    nRBmodKptrs = len(cfg.PRBSet) % cfg.PTRS.FrequencyDensity
    if nRBmodKptrs == 0:
        kRBref = cfg.RNTI % cfg.PTRS.FrequencyDensity
    else:
        kRBref = cfg.RNTI % nRBmodKptrs

    nDmrsPerRE = 6  # DMRSConfigurationType=1 only (this repo's only supported type)

    prbset = np.asarray(cfg.PRBSet[kRBref :: cfg.PTRS.FrequencyDensity])
    return (prbset * nDmrsPerRE) + dmrsRef // 2


def _ptrsSyms(carrier: nrCarrierConfig, cfg: nrPUSCHConfig) -> NDArray[np.int_]:
    """TS 38.211 6.4.1.2.2.1: PT-RS OFDM symbol positions, reset at DM-RS-TypeA-position and at each DM-RS symbol."""
    dmrsSyms = PUSCHDMRSSyms(cfg)
    aPos = cfg.DMRS.DMRSTypeAPosition
    td = cfg.PTRS.TimeDensity

    ptrsCnt = td - 1
    occupiedSyms: list[int] = []
    for i in range(cfg.SymbolAllocation[0], carrier.SymbolsPerSlot):
        if i == aPos or i in dmrsSyms:
            ptrsCnt = 0
            continue

        ptrsCnt += 1
        if ptrsCnt == td:
            occupiedSyms.append(i)
            ptrsCnt = 0

    return np.array(occupiedSyms, dtype=int)


def nrPUSCHPTRS(carrier: nrCarrierConfig, cfg: nrPUSCHConfig) -> NDArray[np.complex128]:
    """Generate PUSCH PT-RS symbols (single-layer, CP-OFDM only)."""
    if cfg.TransformPrecoding == "enabled":
        raise NotImplementedError("Transform-precoded (DFT-s-OFDM) PT-RS is not yet implemented")
    if not cfg.EnablePTRS:
        return np.zeros(0, dtype=np.complex128)

    NSizeBWP = carrier.NSizeGrid if cfg.NSizeBWP is None else cfg.NSizeBWP
    bwpSize = cfg.NRBSize * NSizeBWP

    n_scid = 0
    NIDNSCID = carrier.NCellID if cfg.DMRS.NIDNSCID is None else cfg.DMRS.NIDNSCID
    dmrsOccupiedSyms = PUSCHDMRSSyms(cfg)
    cinitDmrs = PUSCHDMRScinit(carrier.SymbolsPerSlot, carrier.NSlot, int(dmrsOccupiedSyms[0]), NIDNSCID, n_scid)
    dmrsPrbs = nrPRBS(cinitDmrs, bwpSize)
    dmrsSym = nrSymbolModulate(dmrsPrbs, "QPSK")

    ptrsPrbSet = _ptrsPRBSet(cfg)
    ptrsSym = dmrsSym[ptrsPrbSet]

    ptrsOccupiedSyms = _ptrsSyms(carrier, cfg)
    return np.tile(ptrsSym, len(ptrsOccupiedSyms))


def nrPUSCHPTRSIndices(carrier: nrCarrierConfig, cfg: nrPUSCHConfig) -> NDArray[np.int_]:
    """Generate PUSCH PT-RS resource element indices (single-layer, CP-OFDM only)."""
    if cfg.TransformPrecoding == "enabled":
        raise NotImplementedError("Transform-precoded (DFT-s-OFDM) PT-RS is not yet implemented")
    if not cfg.EnablePTRS:
        return np.zeros(0, dtype=int)

    NSizeBWP = carrier.NSizeGrid if cfg.NSizeBWP is None else cfg.NSizeBWP

    frameBegin = cfg.NRBSize * min(cfg.PRBSet)
    frameEnd = cfg.NRBSize * (max(cfg.PRBSet) + 1)
    frameSize = cfg.NRBSize * NSizeBWP

    kRERefTable = [0, 2, 6, 8]  # DMRSConfigurationType=1 only
    kRERef = kRERefTable[int(cfg.PTRS.REOffset, 2)]

    nRBmodKptrs = len(cfg.PRBSet) % cfg.PTRS.FrequencyDensity
    if nRBmodKptrs == 0:
        kRBref = cfg.RNTI % cfg.PTRS.FrequencyDensity
    else:
        kRBref = cfg.RNTI % nRBmodKptrs
    kRBref *= cfg.NRBSize

    ptrsBegin = frameBegin + kRERef + kRBref
    occupiedRes = np.arange(ptrsBegin, frameEnd, cfg.PTRS.FrequencyDensity * cfg.NRBSize)

    occupiedSyms = _ptrsSyms(carrier, cfg)

    if len(occupiedSyms) == 0:
        return np.zeros(0, dtype=int)
    ptrsIndices = np.concatenate([occupiedRes + sym * frameSize for sym in occupiedSyms])
    return ptrsIndices
