import numpy as np

from py3gpp import nrCarrierConfig, nrPUSCHConfig, nrPUSCHIndices


def test_nrPUSCHIndices():
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52

    pusch = nrPUSCHConfig()
    n_size_bwp = 25
    pusch.NSizeBWP = n_size_bwp
    pusch.NStartBWP = 10
    pusch.PRBSet = list(range(n_size_bwp))

    indices = nrPUSCHIndices(carrier, pusch)

    re_per_symbol = pusch.NRBSize * n_size_bwp  # 12 REs/RB * 25 RBs = 300 REs occupied within a symbol
    symbol_stride = carrier.NSizeGrid * pusch.NRBSize  # 12 REs/RB * 52 RBs = 624 REs per symbol in the full grid
    bwp_offset = pusch.NStartBWP * pusch.NRBSize  # 10 RBs * 12 REs/RB = 120
    occupied_syms = pusch.SymbolAllocation[1] - pusch.SymbolAllocation[0]  # 14 symbols
    dmrs_syms = 1  # default config: single DM-RS symbol at DMRSTypeAPosition

    assert indices.dtype.kind == "i"
    assert indices.shape == (re_per_symbol * (occupied_syms - dmrs_syms),)
    assert len(np.unique(indices)) == indices.size, "indices must not contain duplicates"
    assert indices.min() == bwp_offset
    assert indices.max() == bwp_offset + symbol_stride * (occupied_syms - 1) + re_per_symbol - 1

    dmrs_symbol_offset = bwp_offset + 2 * symbol_stride
    assert not np.any((indices >= dmrs_symbol_offset) & (indices < dmrs_symbol_offset + re_per_symbol))
