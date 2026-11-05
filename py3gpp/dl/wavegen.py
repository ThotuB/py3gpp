"""DL carrier orchestration: SSB + CORESET/PDCCH + PDSCH for a single slot, with automatic
ReservedPRB merging so PDSCH structurally avoids SSB/CORESET regions (mirrors the role MATLAB's
nrWaveformGenerator/nrDLCarrierConfig play, scoped to downlink/single-carrier/single-port --
see docs/mathworks_5g_toolbox_coverage.md's Notable gaps for the exact scope cuts)."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from py3gpp.dl.ch.phy.pbch import nrPBCH, nrPBCHIndices
from py3gpp.dl.ch.phy.pdcch import nrCORESETConfig, nrCORESETReservedConfig, nrPDCCH, nrPDCCHConfig, nrPDCCHResources
from py3gpp.dl.ch.phy.pdsch import nrPDSCH, nrPDSCHConfig, nrPDSCHIndices, nrPDSCHReservedConfig
from py3gpp.dl.ch.trs.bch import nrBCH
from py3gpp.dl.ofdm import nrCarrierConfig, nrResourceGrid, nrSetResources
from py3gpp.dl.sig.pbch_dmrs import nrPBCHDMRS, nrPBCHDMRSIndices
from py3gpp.dl.sig.pdsch_dmrs import nrPDSCHDMRS, nrPDSCHDMRSIndices
from py3gpp.dl.sig.pdsch_ptrs import nrPDSCHPTRS, nrPDSCHPTRSIndices
from py3gpp.dl.sig.ss import nrPSS, nrPSSIndices, nrSSS, nrSSSIndices
from py3gpp.dl.sig.ssb import nrSSBurstStartSymbols

_SSB_RB = 20  # SS/PBCH block is always 20 PRBs wide, TS 38.211 7.4.3.1
_SSB_SYMS = 4  # ... and always 4 OFDM symbols
_SSB_SC = 12 * _SSB_RB  # 240, the local flat-index stride PSS/SSS/PBCH/PBCH-DMRS share

_MODULATION_NAME = {"qpsk": "QPSK", "qam16": "16QAM", "qam64": "64QAM", "qam256": "256QAM"}


def _ssbCaseLssb(caseName: str, numBeams: int) -> int:
    case = caseName.removeprefix("Case ").removeprefix("case ").upper()
    if case in ("A", "B", "C"):
        assert numBeams in (4, 8), "TransmittedBlocks length must be 4 or 8 for Case A/B/C"
        return numBeams
    assert numBeams == 64, "TransmittedBlocks length must be 64 for Case D/E/F/G"
    return 64


def _localToGlobal(localInd: NDArray[np.int_], prbOffset: int, startSymbol: int, totalSC: int) -> NDArray[np.int_]:
    """Map a PSS/SSS/PBCH/PBCH-DMRS local (240 sc x 4 sym) flat index into the carrier grid."""
    localSC = localInd % _SSB_SC
    localSym = localInd // _SSB_SC
    globalSC = prbOffset * 12 + localSC
    globalSym = startSymbol + localSym
    return globalSC + globalSym * totalSC


class nrSSBurstConfig:
    """SS/PBCH burst configuration for `nrDLCarrierGenerate` (not a MathWorks-public class --
    MATLAB's nrWavegenSSBurstConfig places SSB by absolute frequency (FrequencySSB), which has no
    equivalent here since nrCarrierConfig has no absolute-frequency concept; PRBOffset is used
    instead). Assumes the SSB's Case-derived SCS matches the carrier's SCS -- no cross-SCS
    rescaling (MATLAB's ssbReservedSymbols) is implemented."""

    def __init__(self) -> None:
        self.Enable: bool = True
        self.BlockPattern: str = "A"
        self.TransmittedBlocks: list[int] = [1, 0, 0, 0, 0, 0, 0, 0]
        self.Period: int = 20  # slots
        self.PRBOffset: int = 0
        self.NCellID: int | None = None
        self.Kssb: int = 0  # Case A/B/C only; the Lssb=64 case embeds the full beam index instead
        self.MIB: list[int] | None = None  # 24-bit BCCH-BCH payload; defaults to all-zero


class nrWavegenPDCCHConfig:
    """PDCCH instance for `nrDLCarrierGenerate`. No AggregationLevel/AllocatedCandidate/payload
    fields exist on the real `nrPDCCHConfig` either (py3gpp has no search-space candidate hashing,
    `nrPDCCHSpace`) -- the caller picks the first CCE directly and supplies already-DCI-encoded
    bits (e.g. via `nrDCIEncode`). Monitoring periodicity comes from
    `PDCCH.SearchSpace.SlotPeriodAndOffset` (real MATLAB field), not a field on this wrapper."""

    def __init__(self) -> None:
        self.PDCCH: nrPDCCHConfig | None = None
        self.CCEStart: int = 0
        self.Bits: NDArray[np.int_] = np.zeros(0, dtype=int)


class nrWavegenPDSCHConfig:
    """PDSCH instance for `nrDLCarrierGenerate`. `ReservedPRB` here is the user's own baseline
    reservation list (kept separate from `PDSCH.ReservedPRB`, which `nrDLCarrierGenerate`
    overwrites fresh on every call -- reading it back in would accumulate duplicates across
    repeated calls with the same config, e.g. when generating multiple slots)."""

    def __init__(self) -> None:
        self.PDSCH: nrPDSCHConfig = nrPDSCHConfig()
        self.Period: int = 1  # slots
        self.ReservedCORESET: list[int] = []
        self.ReservedPRB: list[nrPDSCHReservedConfig] = []
        self.Codeword: NDArray[np.int_] = np.zeros(0, dtype=int)


class nrDLCarrierConfig:
    """Top-level container for `nrDLCarrierGenerate`: a single carrier/BWP, optional SSB burst,
    a set of CORESETs, and the PDCCH/PDSCH instances to place in it."""

    def __init__(self) -> None:
        self.Carrier: nrCarrierConfig = nrCarrierConfig()
        self.SSBurst: nrSSBurstConfig | None = None
        self.CORESET: list[nrCORESETConfig] = []
        self.PDCCH: list[nrWavegenPDCCHConfig] = []
        self.PDSCH: list[nrWavegenPDSCHConfig] = []


def _generateSSB(
    carrier: nrCarrierConfig, ssb: nrSSBurstConfig, nSlot: int
) -> tuple[NDArray[np.int_], NDArray[np.complex128], list[dict], list[nrPDSCHReservedConfig]]:
    totalSC = 12 * carrier.NSizeGrid
    ncellid = carrier.NCellID if ssb.NCellID is None else ssb.NCellID
    numBeams = len(ssb.TransmittedBlocks)
    lssb = _ssbCaseLssb(ssb.BlockPattern, numBeams)
    startSymbols = nrSSBurstStartSymbols(ssb.BlockPattern, lssb)

    symPerSlot = carrier.SymbolsPerSlot
    halfFrameStart = (nSlot // ssb.Period) * ssb.Period
    relSlot = nSlot - halfFrameStart

    sfn = carrier.NFrame
    hrf = (nSlot // carrier.SlotsPerFrame) % 2
    v = 2 * ((sfn >> 2) & 1) + ((sfn >> 1) & 1)
    mib = np.zeros(24, dtype=int) if ssb.MIB is None else np.asarray(ssb.MIB, dtype=int)

    indices = []
    beams: list[dict] = []
    reservations: list[nrPDSCHReservedConfig] = []

    for beamIdx, on in enumerate(ssb.TransmittedBlocks):
        if not on:
            # Only actually-transmitted positions (ssb-PositionsInBurst) are off-limits to
            # PDSCH -- an untransmitted candidate position is free for the scheduler to use.
            continue

        rsv = nrPDSCHReservedConfig()
        rsv.PRBSet = list(range(ssb.PRBOffset, ssb.PRBOffset + _SSB_RB))
        absSym = int(startSymbols[beamIdx])
        rsv.SymbolSet = [absSym + k for k in range(_SSB_SYMS)]
        rsv.Period = ssb.Period
        reservations.append(rsv)

        if absSym // symPerSlot != relSlot:
            continue
        startSymbol = absSym % symPerSlot

        idxoffset = beamIdx if lssb == 64 else ssb.Kssb
        ibarSSB = beamIdx % 8
        codedBits = nrBCH(mib, sfn, hrf, lssb, idxoffset, ncellid)
        pbchSym = nrPBCH(ncellid, v, codedBits)
        pbchDmrsSym = nrPBCHDMRS(ncellid, ibarSSB)

        pssInd = _localToGlobal(nrPSSIndices(), ssb.PRBOffset, startSymbol, totalSC)
        sssInd = _localToGlobal(nrSSSIndices(), ssb.PRBOffset, startSymbol, totalSC)
        pbchInd = _localToGlobal(nrPBCHIndices(ncellid), ssb.PRBOffset, startSymbol, totalSC)
        pbchDmrsLocalInd = nrPBCHDMRSIndices(ncellid, style="matlab")
        assert isinstance(pbchDmrsLocalInd, np.ndarray)
        pbchDmrsInd = _localToGlobal(pbchDmrsLocalInd, ssb.PRBOffset, startSymbol, totalSC)

        indices.append((pssInd, nrPSS(ncellid).astype(complex)))
        indices.append((sssInd, nrSSS(ncellid).astype(complex)))
        indices.append((pbchInd, pbchSym))
        indices.append((pbchDmrsInd, pbchDmrsSym))

        beams.append(
            {
                "beamIndex": beamIdx,
                "PSS": pssInd,
                "SSS": sssInd,
                "PBCH": pbchInd,
                "PBCHDMRS": pbchDmrsInd,
            }
        )

    allInd = np.concatenate([ind for ind, _ in indices]) if indices else np.zeros(0, dtype=int)
    allVals = np.concatenate([val for _, val in indices]) if indices else np.zeros(0, dtype=complex)
    return allInd.astype(int), allVals, beams, reservations


def nrDLCarrierGenerate(cfgObj: nrDLCarrierConfig, nSlot: int) -> tuple[NDArray[np.complex128], dict[str, list]]:
    """Generate one slot's downlink resource grid from an `nrDLCarrierConfig`: places SSB (if
    configured), PDCCH, and PDSCH, with every PDSCH instance's `ReservedPRB` automatically merged
    from the active SSB beams' footprints and its own `ReservedCORESET` list -- so PDSCH
    structurally avoids both without the caller hand-building the reservation list.

    Returns (grid, info), where info["SSB"]/info["PDCCH"]/info["PDSCH"] list per-instance index
    dicts, so a caller (e.g. a resource-grid visualizer) can identify which REs belong to which
    channel/beam without re-deriving them.
    """
    carrier = cfgObj.Carrier
    carrier.NSlot = nSlot
    grid = nrResourceGrid(carrier)
    info: dict[str, list] = {"SSB": [], "PDCCH": [], "PDSCH": []}

    ssbReservations: list[nrPDSCHReservedConfig] = []
    if cfgObj.SSBurst is not None and cfgObj.SSBurst.Enable:
        ind, vals, beams, ssbReservations = _generateSSB(carrier, cfgObj.SSBurst, nSlot)
        if ind.size:
            nrSetResources(ind, grid, vals)
        info["SSB"] = beams

    # CORESET.ControlResourceSetId -> its SearchSpace's StartSymbolWithinSlot (real MATLAB keeps
    # this on nrSearchSpaceConfig, not the CORESET itself -- see nrPDCCHResources' docstring).
    # Used both for PDCCH's own generation below and for building matching PDSCH reservations.
    coresetStartSymbols: dict[int, int] = {
        pdcch.PDCCH.SearchSpace.ControlResourceSetId: pdcch.PDCCH.SearchSpace.StartSymbolWithinSlot
        for pdcch in cfgObj.PDCCH
        if pdcch.PDCCH is not None
    }
    # Same idea for periodicity: a CORESET is only actually monitored (and so only actually
    # needs excluding from PDSCH) on the slots its own search space is monitored on. Default to
    # every slot ((1, 0)) for a CORESET no configured PDCCH references, since that's the safe
    # assumption.
    coresetPeriods: dict[int, tuple[int, int]] = {
        pdcch.PDCCH.SearchSpace.ControlResourceSetId: pdcch.PDCCH.SearchSpace.SlotPeriodAndOffset
        for pdcch in cfgObj.PDCCH
        if pdcch.PDCCH is not None
    }

    for pdcch in cfgObj.PDCCH:
        if pdcch.PDCCH is None:
            continue
        period, offset = pdcch.PDCCH.SearchSpace.SlotPeriodAndOffset
        if nSlot % period != offset:
            continue
        # 1 CCE = 6 REGs; each REG has 9 data REs (12 - 3 DM-RS), QPSK -> 6*9*2 = 108 bits/CCE.
        aggLevel = max(1, len(pdcch.Bits) // 108)
        cceIndices = list(range(pdcch.CCEStart, pdcch.CCEStart + aggLevel))
        startSymbol = pdcch.PDCCH.SearchSpace.StartSymbolWithinSlot
        contentInd, dmrsInd = nrPDCCHResources(carrier, pdcch.PDCCH.CORESET, cceIndices, startSymbol)
        sym = nrPDCCH(pdcch.Bits, pdcch.PDCCH.RNTI, pdcch.PDCCH.CORESET.ControlResourceSetId)
        nrSetResources(contentInd, grid, sym)
        info["PDCCH"].append({"indices": contentInd, "dmrsIndices": dmrsInd})

    for pdsch in cfgObj.PDSCH:
        if nSlot % pdsch.Period != 0:
            continue
        coresetReservations = []
        for cid in pdsch.ReservedCORESET:
            ctrlId = cfgObj.CORESET[cid].ControlResourceSetId
            rsv = nrCORESETReservedConfig(cfgObj.CORESET[cid], coresetStartSymbols.get(ctrlId, 0))
            rsv.Period, rsv.Offset = coresetPeriods.get(ctrlId, (1, 0))
            coresetReservations.append(rsv)
        pdsch.PDSCH.ReservedPRB = ssbReservations + coresetReservations + list(pdsch.ReservedPRB)

        ind = nrPDSCHIndices(carrier, pdsch.PDSCH)
        modName = _MODULATION_NAME[pdsch.PDSCH.Modulation]
        sym = nrPDSCH([pdsch.Codeword], [modName], pdsch.PDSCH.NumLayers, pdsch.PDSCH.Nid, pdsch.PDSCH.RNTI)[0]
        nrSetResources(ind, grid, sym[: len(ind)])

        dmrsInd = nrPDSCHDMRSIndices(carrier, pdsch.PDSCH)
        dmrsSym = nrPDSCHDMRS(pdsch.PDSCH, carrier)
        nrSetResources(dmrsInd, grid, dmrsSym)

        entry = {"indices": ind, "dmrsIndices": dmrsInd}
        if pdsch.PDSCH.EnablePTRS:
            ptrsInd = nrPDSCHPTRSIndices(carrier, pdsch.PDSCH)
            ptrsSym = nrPDSCHPTRS(carrier, pdsch.PDSCH)
            nrSetResources(np.asarray(ptrsInd, dtype=int), grid, np.asarray(ptrsSym))
            entry["ptrsIndices"] = ptrsInd
        info["PDSCH"].append(entry)

    return grid, info
