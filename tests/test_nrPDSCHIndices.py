import numpy as np

from py3gpp import nrCarrierConfig, nrPDSCHConfig, nrPDSCHIndices


def test_nrPDSCHIndices():
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52

    pdsch = nrPDSCHConfig()
    n_size_bwp = 25
    pdsch.NSizeBWP = n_size_bwp
    pdsch.NStartBWP = 10
    pdsch.PRBSet = list(range(n_size_bwp))

    indices = nrPDSCHIndices(carrier, pdsch)

    re_per_symbol = pdsch.NRBSize * n_size_bwp  # 12 REs/RB * 25 RBs = 300 REs occupied within a symbol
    symbol_stride = carrier.NSizeGrid * pdsch.NRBSize  # 12 REs/RB * 52 RBs = 624 REs per symbol in the full grid
    bwp_offset = pdsch.NStartBWP * pdsch.NRBSize  # 10 RBs * 12 REs/RB = 120
    occupied_syms = pdsch.SymbolAllocation[1] - pdsch.SymbolAllocation[0]  # 14 symbols
    dmrs_syms = 1  # default config: single DM-RS symbol at DMRSTypeAPosition

    assert indices.dtype.kind == "i"
    assert indices.shape == (re_per_symbol * (occupied_syms - dmrs_syms),)
    assert len(np.unique(indices)) == indices.size, "indices must not contain duplicates"
    assert indices.min() == bwp_offset
    assert indices.max() == bwp_offset + symbol_stride * (occupied_syms - 1) + re_per_symbol - 1

    # the DM-RS symbol (symbol index 2, the default DMRSTypeAPosition) must be excluded entirely
    dmrs_symbol_offset = bwp_offset + 2 * symbol_stride
    assert not np.any((indices >= dmrs_symbol_offset) & (indices < dmrs_symbol_offset + re_per_symbol))
