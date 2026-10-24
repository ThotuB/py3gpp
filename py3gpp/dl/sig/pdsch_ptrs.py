# 38.211
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from numpy.typing import NDArray

from py3gpp.dl.ofdm import nrCarrierConfig
from py3gpp.dl.sig.pdsch_dmrs import PDSCHDMRSSyms
from py3gpp.plc.sym import nrPRBS, nrSymbolModulate

if TYPE_CHECKING:
    # imported only for type hints: avoids a circular import, since nrPDSCHConfig's
    # home module (dl.ch.phy.pdsch) itself imports PDSCHDMRSSyms from dl.sig.pdsch_dmrs
    from py3gpp.dl.ch.phy.pdsch import nrPDSCHConfig


def nrPDSCHPTRS(carrier: nrCarrierConfig, cfg: nrPDSCHConfig) -> list | NDArray[np.complex128]:
    if cfg.EnablePTRS == 0:
        return []

    bwp_size = cfg.NRBSize * cfg.NSizeBWP

    # Generates first DMRS symbol (l0)
    n_scid = 0
    dmrs_occupied_syms = PDSCHDMRSSyms(cfg)
    cinit_dmrs = PDSCHPTRScinit(carrier.SymbolsPerSlot, carrier.NSlot, dmrs_occupied_syms[0], cfg.DMRS.NIDNSCID, n_scid)
    dmrs_prbs = nrPRBS(cinit_dmrs, bwp_size)
    dmrs_sym = nrSymbolModulate(dmrs_prbs, "QPSK")

    # Form PTRS symbols from DMRS l0 sequency
    ptrs_prb_set = PTRSPRBSet(cfg)

    ptrs_sym = np.array([dmrs_sym[x] for x in ptrs_prb_set])

    ptrs_occupied_syms = PDSCHPTRSSyms(carrier, cfg)

    return np.tile(ptrs_sym, len(ptrs_occupied_syms))


def PTRSPRBSet(cfg: nrPDSCHConfig) -> NDArray[Any]:
    # Align with frequency offset based on DMRS type
    if cfg.DMRS.DMRSConfigurationType == 1:
        dmrs_ref_table = np.array([0, 2, 6, 8])
    else:
        dmrs_ref_table = np.array([0, 2, 4, 6])
    kRE_idx = int(cfg.PTRS.REOffset, 2)
    dmrsRef = dmrs_ref_table[kRE_idx]

    Nrb_mod_Kptrs = len(cfg.PRBSet) % cfg.PTRS.FrequencyDensity
    if Nrb_mod_Kptrs == 0:
        kRBref = cfg.RNTI % cfg.PTRS.FrequencyDensity
    else:
        kRBref = cfg.RNTI % Nrb_mod_Kptrs

    if cfg.DMRS.DMRSConfigurationType == 1:
        n_dmrs_per_re = 6
    else:
        n_dmrs_per_re = 4

    prb_set = np.array(cfg.PRBSet[kRBref :: cfg.PTRS.FrequencyDensity])
    prb_set = (prb_set * n_dmrs_per_re) + dmrsRef // 2

    return prb_set


# LUT for PTRS occupied symbols positions
def PDSCHPTRSSyms(carrier: nrCarrierConfig, cfg: nrPDSCHConfig) -> NDArray[np.int_]:
    # First get DMRS symbols
    dmrs_syms = PDSCHDMRSSyms(cfg)
    # Then calculate positions of PTRS
    A_pos = cfg.DMRS.DMRSTypeAPosition
    td = cfg.PTRS.TimeDensity

    ptrs_cnt = td - 1
    occupied_syms = np.array([], dtype=int)
    for i in range(cfg.SymbolAllocation[0], carrier.SymbolsPerSlot):
        if i == A_pos:
            ptrs_cnt = 0
            continue

        if i in dmrs_syms:
            ptrs_cnt = 0
            continue

        ptrs_cnt += 1

        if ptrs_cnt == td:
            occupied_syms = np.append(occupied_syms, i)
            ptrs_cnt = 0

    return occupied_syms


def PDSCHPTRScinit(sps: int, n_slot: int, n_symb: int, NIDSCID: int, n_scid: int) -> int:
    return 2**17 * (sps * n_slot + n_symb + 1) * (2 * NIDSCID + 1) + 2 * NIDSCID + n_scid


def nrPDSCHPTRSIndices(carrier: nrCarrierConfig, cfg: nrPDSCHConfig) -> NDArray[Any]:
    if cfg.EnablePTRS == 0:
        return np.array([])

    frame_begin = cfg.NRBSize * min(cfg.PRBSet)
    frame_end = cfg.NRBSize * (max(cfg.PRBSet) + 1)
    frame_size = cfg.NRBSize * cfg.NSizeBWP

    # Align with frequency offset based on DMRS type
    if cfg.DMRS.DMRSConfigurationType == 1:
        kREref_table = [0, 2, 6, 8]
    else:
        kREref_table = [0, 1, 6, 7]
    kREref = kREref_table[int(cfg.PTRS.REOffset, 2)]

    Nrb_mod_Kptrs = len(cfg.PRBSet) % cfg.PTRS.FrequencyDensity
    if Nrb_mod_Kptrs == 0:
        kRBref = cfg.RNTI % cfg.PTRS.FrequencyDensity
    else:
        kRBref = cfg.RNTI % Nrb_mod_Kptrs
    kRBref *= cfg.NRBSize

    # Move to BWP offset and the rest frequency offsets
    ptrs_begin = frame_begin + kREref + kRBref

    # Calculate PTRS positions in every occupied symbol. Frequency position,
    # for every 2 or 4 RBs
    occupied_res = np.array(list(range(ptrs_begin, frame_end, (cfg.PTRS.FrequencyDensity * cfg.NRBSize))))

    # Calculates occupied symbols numbers. Time positions
    occupied_syms = PDSCHPTRSSyms(carrier, cfg)

    # Move PTRS indices to occupied symbols
    ptrs_indices = np.array([occupied_res + (sym * frame_size) for sym in occupied_syms])
    if len(ptrs_indices) > 0:
        ptrs_indices = np.concatenate(ptrs_indices, axis=None)

    return ptrs_indices
