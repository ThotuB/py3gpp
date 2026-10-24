import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrCSIRS, nrCSIRSConfig, nrCSIRSIndices


def _carrier(n_size_grid: int = 52) -> nrCarrierConfig:
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = n_size_grid
    return carrier


@pytest.mark.parametrize("row,density,kwargs", [(1, "three", {}), (2, "one", {"SubcarrierLocations": 3})])
def test_nrCSIRS_single_port_rows(row, density, kwargs):
    carrier = _carrier()
    csirs = nrCSIRSConfig()
    csirs.RowNumber = row
    csirs.Density = density
    csirs.NumRB = 5
    csirs.SymbolLocations = 1
    for k, v in kwargs.items():
        setattr(csirs, k, v)

    indices = nrCSIRSIndices(carrier, csirs)
    syms = nrCSIRS(carrier, csirs)

    assert syms.dtype == np.complex128
    assert syms.shape == indices.shape
    assert np.allclose(np.abs(syms), 1.0)  # unit-magnitude QPSK

    # deterministic: re-generating with identical config gives identical output
    assert np.array_equal(syms, nrCSIRS(carrier, csirs))


def test_nrCSIRS_row3_two_port_occ():
    carrier = _carrier()
    csirs = nrCSIRSConfig()
    csirs.RowNumber = 3
    csirs.Density = "one"
    csirs.NumRB = 4
    csirs.SubcarrierLocations = 2
    csirs.SymbolLocations = 3

    indices = nrCSIRSIndices(carrier, csirs)
    syms = nrCSIRS(carrier, csirs)

    assert syms.dtype == np.complex128
    assert syms.shape == indices.shape
    assert np.allclose(np.abs(syms), 1.0)

    n = len(syms) // 2
    port0, port1 = syms[:n], syms[n:]
    # TS 38.211 Table 7.4.1.5.3-3 fd-CDM2 OCC: w_f(0)=[+1,+1], w_f(1)=[+1,-1]
    assert np.allclose(port0[0::2], port1[0::2])  # k'=0: both ports agree
    assert np.allclose(port0[1::2], -port1[1::2])  # k'=1: port 1 is negated


def test_nrCSIRS_zp_not_implemented():
    carrier = _carrier()
    csirs = nrCSIRSConfig()
    csirs.CSIRSType = "ZP"

    with pytest.raises(NotImplementedError):
        nrCSIRS(carrier, csirs)


def test_nrCSIRS_rows_above_3_not_implemented():
    carrier = _carrier()
    csirs = nrCSIRSConfig()
    csirs.RowNumber = 5

    with pytest.raises(NotImplementedError):
        nrCSIRS(carrier, csirs)
