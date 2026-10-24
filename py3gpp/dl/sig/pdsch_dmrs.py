# 38.211
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from py3gpp.dl.ofdm import nrCarrierConfig
from py3gpp.plc.sym import nrPRBS, nrSymbolModulate

if TYPE_CHECKING:
    # imported only for type hints: avoids a circular import, since nrPDSCHConfig's
    # home module (dl.ch.phy.pdsch) itself imports PDSCHDMRSSyms from this file
    from py3gpp.dl.ch.phy.pdsch import nrPDSCHConfig


def nrPDSCHDMRS(cfg: nrPDSCHConfig, carrier: nrCarrierConfig) -> NDArray[np.complex128]:
    if cfg.DMRS.DMRSConfigurationType == 1:
        n_dmrs_per_re = 6
    else:
        n_dmrs_per_re = 4
    n_dmrs_bits_re = 2 * n_dmrs_per_re

    dmrs_begin = n_dmrs_bits_re * min(cfg.PRBSet)
    dmrs_end = n_dmrs_bits_re * (max(cfg.PRBSet) + 1)
    dmrs_size = n_dmrs_bits_re * cfg.NSizeBWP

    n_scid = 0

    occupied_syms = PDSCHDMRSSyms(cfg)

    # Start generation for every symbol
    dmrs_syms = np.array([])
    for n_symb in occupied_syms:
        cinit_dmrs = PDSCHDMRScinit(carrier.SymbolsPerSlot, carrier.NSlot, n_symb, cfg.DMRS.NIDNSCID, n_scid)
        dmrs_prbs = nrPRBS(cinit_dmrs, dmrs_size)

        # Cut PRBS sequency
        dmrs_prbs = dmrs_prbs[dmrs_begin:dmrs_end]
        dmrs_syms = np.append(dmrs_syms, nrSymbolModulate(dmrs_prbs, "QPSK"))

    return dmrs_syms


# LUT for DMRS occupied symbols positions
def PDSCHDMRSSyms(cfg: nrPDSCHConfig) -> NDArray[np.int_]:
    assert cfg.MappingType in ["A"], "Mapping type B is not yet implemented"
    l1 = 11
    typeA_pos = cfg.DMRS.DMRSTypeAPosition
    sym_alloc = cfg.SymbolAllocation[1]
    add_pos = cfg.DMRS.DMRSAdditionalPosition
    dmrs_len = cfg.DMRS.DMRSLength

    occupied_syms = np.array([typeA_pos], dtype=int)

    if dmrs_len == 1:  # Table 7.4.1.1.2-3, Type A
        if sym_alloc in [8, 9]:
            if add_pos > 0:
                occupied_syms = np.append(occupied_syms, 7)
        elif sym_alloc in [10, 11]:
            if add_pos == 1:
                occupied_syms = np.append(occupied_syms, 9)
            elif add_pos == 2 or add_pos == 3:
                occupied_syms = np.append(occupied_syms, [6, 9])
        elif sym_alloc == 12:
            if add_pos == 1:
                occupied_syms = np.append(occupied_syms, 9)
            elif add_pos == 2:
                occupied_syms = np.append(occupied_syms, [6, 9])
            elif add_pos == 3:
                occupied_syms = np.append(occupied_syms, [5, 8, 11])
        elif sym_alloc in [13, 14]:
            if add_pos == 1:
                occupied_syms = np.append(occupied_syms, l1)
            elif add_pos == 2:
                occupied_syms = np.append(occupied_syms, [7, 11])
            elif add_pos == 3:
                occupied_syms = np.append(occupied_syms, [5, 8, 11])
    else:  # Table 7.4.1.1.2-4, Type A
        if add_pos == 1:
            if sym_alloc in [10, 11, 12]:
                occupied_syms = np.append(occupied_syms, 8)
            elif sym_alloc in [13, 14]:
                occupied_syms = np.append(occupied_syms, 10)
        elif add_pos > 1:
            raise ValueError("add_pos has to be [0, 1] for double-symbol")

        occupied_syms = np.concatenate((occupied_syms[np.newaxis], occupied_syms[np.newaxis] + 1), axis=0).T.ravel()

    return occupied_syms


def PDSCHDMRScinit(sps: int, n_slot: int, n_symb: int, NIDSCID: int, n_scid: int) -> int:
    return 2**17 * (sps * n_slot + n_symb + 1) * (2 * NIDSCID + 1) + 2 * NIDSCID + n_scid


def nrPDSCHDMRSIndices(carrier: nrCarrierConfig, cfg: nrPDSCHConfig) -> NDArray[np.int_]:
    NRBSize = carrier.NStartGrid if not cfg.NRBSize else cfg.NRBSize
    NSizeBWP = carrier.NSizeGrid if not cfg.NSizeBWP else cfg.NSizeBWP

    frame_begin = NRBSize * min(cfg.PRBSet)
    frame_end = NRBSize * (max(cfg.PRBSet) + 1)
    frame_size = NRBSize * NSizeBWP

    # Single frame DMRS positions
    dmrs_full_range = np.array(list(range(frame_begin, frame_end)))

    # Calculate DMRS positions in every occupied symbol. Frequency position
    if cfg.DMRS.DMRSConfigurationType == 1:
        # Takes every 2nd symbol
        occupied_res = dmrs_full_range[::2]
    elif cfg.DMRS.DMRSConfigurationType == 2:
        # Takes every 4th couple of symbols
        occupied_res = dmrs_full_range.reshape(-1, 2)[::3].ravel()

    # Calculates occupied symbols numbers. Time positions
    occupied_syms = PDSCHDMRSSyms(cfg)

    dmrs_indices = np.array([], int)
    for idx, sym in enumerate(occupied_syms):
        sym_offset = sym * frame_size
        dmrs_indices = np.append(dmrs_indices, (occupied_res + sym_offset))

    return dmrs_indices
