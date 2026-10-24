import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrCSIRSConfig, nrCSIRSIndices


def _carrier(n_size_grid: int = 52) -> nrCarrierConfig:
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = n_size_grid
    return carrier


def test_nrCSIRSIndices_row1_fixed_k_positions():
    carrier = _carrier()
    csirs = nrCSIRSConfig()
    csirs.RowNumber = 1
    csirs.Density = "three"
    csirs.NumRB = 1
    csirs.SymbolLocations = 5

    indices = nrCSIRSIndices(carrier, csirs)
    sym_offset = 5 * 12 * carrier.NSizeGrid
    assert indices.tolist() == [sym_offset, sym_offset + 4, sym_offset + 8]


def test_nrCSIRSIndices_row2_configurable_k():
    carrier = _carrier()
    csirs = nrCSIRSConfig()
    csirs.RowNumber = 2
    csirs.Density = "one"
    csirs.NumRB = 1
    csirs.SubcarrierLocations = 7
    csirs.SymbolLocations = 2

    indices = nrCSIRSIndices(carrier, csirs)
    sym_offset = 2 * 12 * carrier.NSizeGrid
    assert indices.tolist() == [sym_offset + 7]


def test_nrCSIRSIndices_row1_repeats_across_rb():
    carrier = _carrier()
    csirs = nrCSIRSConfig()
    csirs.RowNumber = 1
    csirs.Density = "three"
    csirs.NumRB = 4
    csirs.RBOffset = 2
    csirs.SymbolLocations = 0

    indices = nrCSIRSIndices(carrier, csirs)
    expected = np.concatenate([np.array([0, 4, 8]) + 12 * rb for rb in range(2, 6)])
    assert indices.tolist() == expected.tolist()
    assert len(np.unique(indices)) == indices.size


def test_nrCSIRSIndices_row3_two_ports_same_res_different_plane():
    carrier = _carrier()
    csirs = nrCSIRSConfig()
    csirs.RowNumber = 3
    csirs.Density = "one"
    csirs.NumRB = 3
    csirs.SubcarrierLocations = 4
    csirs.SymbolLocations = 0

    indices = nrCSIRSIndices(carrier, csirs)
    assert indices.shape == (2 * 2 * csirs.NumRB,)  # 2 ports * (k, k+1) pair * NumRB

    totalSC = 12 * carrier.NSizeGrid
    totalSyms = carrier.SymbolsPerSlot
    port_stride = totalSC * totalSyms

    n = len(indices) // 2
    port0, port1 = indices[:n], indices[n:]
    assert np.array_equal(port1 - port0, np.full(n, port_stride))
    assert len(np.unique(indices)) == indices.size

    # within one port, the (k, k+1) pair per RB is covered and no RE lies outside [0, 11] of its RB
    for rb in range(csirs.NumRB):
        base = rb * 12 + csirs.SubcarrierLocations
        assert base in port0 and (base + 1) in port0


def test_nrCSIRSIndices_subcarrier_locations_must_be_even_for_row3():
    carrier = _carrier()
    csirs = nrCSIRSConfig()
    csirs.RowNumber = 3
    csirs.Density = "one"
    csirs.SubcarrierLocations = 5  # odd -> invalid for a (k, k+1) CDM pair

    with pytest.raises(AssertionError):
        nrCSIRSIndices(carrier, csirs)


def test_nrCSIRSIndices_row_density_mismatch_asserts():
    carrier = _carrier()
    csirs = nrCSIRSConfig()
    csirs.RowNumber = 1
    csirs.Density = "one"  # Row 1 requires 'three'

    with pytest.raises(AssertionError):
        nrCSIRSIndices(carrier, csirs)


def test_nrCSIRSIndices_rows_above_3_not_implemented():
    carrier = _carrier()
    csirs = nrCSIRSConfig()
    csirs.RowNumber = 4

    with pytest.raises(NotImplementedError):
        nrCSIRSIndices(carrier, csirs)


def test_nrCSIRSIndices_zp_not_implemented():
    carrier = _carrier()
    csirs = nrCSIRSConfig()
    csirs.CSIRSType = "ZP"

    with pytest.raises(NotImplementedError):
        nrCSIRSIndices(carrier, csirs)
