# Ref: TS 38.211 Section 7.4.1.5
from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from py3gpp.dl.ofdm import nrCarrierConfig
from py3gpp.plc.sym import nrPRBS, nrSymbolModulate


class nrCSIRSConfig:
    """CSI-RS configuration parameters."""

    def __init__(self) -> None:
        self._RowNumber: int = 1
        self._Density: Literal["three", "dot5even", "dot5odd", "one"] = "one"
        self._NumRB: int | None = None
        self._RBOffset: int = 0
        self._SubcarrierLocations: int = 0
        self._SymbolLocations: int = 0
        self._NID: int | None = None
        self._CSIRSType: Literal["ZP", "NZP"] = "NZP"

    @property
    def RowNumber(self) -> int:
        return self._RowNumber

    @RowNumber.setter
    def RowNumber(self, value: int) -> None:
        assert 1 <= value <= 18, "The value must be 1..18"
        self._RowNumber = value

    @property
    def Density(self) -> Literal["three", "dot5even", "dot5odd", "one"]:
        return self._Density

    @Density.setter
    def Density(self, value: Literal["three", "dot5even", "dot5odd", "one"]) -> None:
        assert value in (
            "three",
            "dot5even",
            "dot5odd",
            "one",
        ), "The value must be 'three', 'dot5even', 'dot5odd', or 'one'"
        self._Density = value

    @property
    def NumRB(self) -> int | None:
        return self._NumRB

    @NumRB.setter
    def NumRB(self, value: int) -> None:
        assert value > 0, "The value must be > 0"
        self._NumRB = value

    @property
    def RBOffset(self) -> int:
        return self._RBOffset

    @RBOffset.setter
    def RBOffset(self, value: int) -> None:
        assert value >= 0, "The value must be >= 0"
        self._RBOffset = value

    @property
    def SubcarrierLocations(self) -> int:
        return self._SubcarrierLocations

    @SubcarrierLocations.setter
    def SubcarrierLocations(self, value: int) -> None:
        assert 0 <= value <= 11, "The value must be 0..11"
        self._SubcarrierLocations = value

    @property
    def SymbolLocations(self) -> int:
        return self._SymbolLocations

    @SymbolLocations.setter
    def SymbolLocations(self, value: int) -> None:
        assert 0 <= value <= 13, "The value must be 0..13"
        self._SymbolLocations = value

    @property
    def NID(self) -> int | None:
        return self._NID

    @NID.setter
    def NID(self, value: int) -> None:
        assert 0 <= value <= 1007, "The value must be 0..1007"
        self._NID = value

    @property
    def CSIRSType(self) -> Literal["ZP", "NZP"]:
        return self._CSIRSType

    @CSIRSType.setter
    def CSIRSType(self, value: Literal["ZP", "NZP"]) -> None:
        assert value in ("ZP", "NZP"), "The value must be 'ZP' or 'NZP'"
        self._CSIRSType = value


# Rows 4-18 (4/8/12/16/24/32-port, CDM4/CDM8, multi-frequency-group patterns) are not
# implemented: the exact k-offset combinations in TS 38.211 Table 7.4.1.5.3-1 could not
# be verified without a live MATLAB session or the spec text itself.
_NUM_PORTS = {1: 1, 2: 1, 3: 2}


def _rowKPositions(csirs: nrCSIRSConfig) -> list[int]:
    """Resolve (RowNumber, Density, SubcarrierLocations) into within-RB k offsets."""
    if csirs.RowNumber == 1:
        assert csirs.Density == "three", "Row 1 requires Density='three'"
        return [0, 4, 8]
    elif csirs.RowNumber == 2:
        assert csirs.Density == "one", "Row 2 requires Density='one'"
        return [csirs.SubcarrierLocations]
    elif csirs.RowNumber == 3:
        assert csirs.Density == "one", "Row 3 requires Density='one'"
        assert csirs.SubcarrierLocations % 2 == 0, "Row 3 requires an even SubcarrierLocations (0, 2, 4, 6, 8, or 10)"
        return [csirs.SubcarrierLocations, csirs.SubcarrierLocations + 1]
    else:
        raise NotImplementedError("RowNumber > 3 is not yet implemented")


def nrCSIRScinit(sps: int, n_slot: int, n_symb: int, nid: int) -> int:
    """TS 38.211 7.4.1.5.2 CSI-RS sequence initialization value."""
    return (2**10 * (sps * n_slot + n_symb + 1) * (2 * nid + 1) + nid) % 2**31


def nrCSIRSIndices(carrier: nrCarrierConfig, csirs: nrCSIRSConfig) -> NDArray[np.int_]:
    """Generate CSI-RS resource element indices."""
    if csirs.CSIRSType == "ZP":
        raise NotImplementedError("ZP CSI-RS is not yet implemented")

    k_positions = _rowKPositions(csirs)
    n_ports = _NUM_PORTS[csirs.RowNumber]
    NumRB = carrier.NSizeGrid if csirs.NumRB is None else csirs.NumRB

    rb_range = np.arange(csirs.RBOffset, csirs.RBOffset + NumRB)
    k_offsets = np.array(k_positions)
    # one RE per (RB, k offset) pair, RB-major / k-minor order
    subcarriers = (rb_range[:, None] * 12 + k_offsets[None, :]).ravel()

    totalSC = 12 * carrier.NSizeGrid
    totalSyms = carrier.SymbolsPerSlot
    base_indices = subcarriers + csirs.SymbolLocations * totalSC

    port_stride = totalSC * totalSyms
    indices = np.concatenate([base_indices + p * port_stride for p in range(n_ports)])
    return indices.astype(int)


def nrCSIRS(carrier: nrCarrierConfig, csirs: nrCSIRSConfig) -> NDArray[np.complex128]:
    """Generate CSI-RS symbols."""
    if csirs.CSIRSType == "ZP":
        raise NotImplementedError("ZP CSI-RS is not yet implemented")

    k_positions = _rowKPositions(csirs)
    n_ports = _NUM_PORTS[csirs.RowNumber]
    NumRB = carrier.NSizeGrid if csirs.NumRB is None else csirs.NumRB
    nid = carrier.NCellID if csirs.NID is None else csirs.NID

    cinit = nrCSIRScinit(carrier.SymbolsPerSlot, carrier.NSlot, csirs.SymbolLocations, nid)

    if csirs.RowNumber == 3:
        # TS 38.211 Table 7.4.1.5.3-3 (fd-CDM2): one base QPSK symbol per RB, shared by the
        # (k, k+1) RE pair, weighted per port by the frequency-domain OCC w_f(k').
        base = nrSymbolModulate(nrPRBS(cinit, 2 * NumRB), "qpsk")
        occ = ((1, 1), (1, -1))  # occ[k_prime][port]
        return np.concatenate([np.stack([base * occ[0][p], base * occ[1][p]], axis=-1).ravel() for p in range(n_ports)])

    return nrSymbolModulate(nrPRBS(cinit, 2 * NumRB * len(k_positions)), "qpsk")
