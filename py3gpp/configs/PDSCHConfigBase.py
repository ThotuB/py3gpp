from __future__ import annotations

from typing import Literal

from .nrPDSCHDMRSConfig import nrPDSCHDMRSConfig
from .nrPDSCHPTRSConfig import nrPDSCHPTRSConfig


class PDSCHConfigBase:
    def __init__(self) -> None:
        self._Modulation: Literal["qpsk", "qam16", "qam64", "qam256"] = "qpsk"
        self._NumLayers: int = 1
        self._ReservedPRB: None = None
        self._VRBToPRBInterleaving: int = 0
        self._VRBBundleSize: int = 2

        self.DMRS: nrPDSCHDMRSConfig = nrPDSCHDMRSConfig()
        self.PTRS: nrPDSCHPTRSConfig = nrPDSCHPTRSConfig()

    @property
    def Modulation(self) -> Literal["qpsk", "qam16", "qam64", "qam256"]:
        return self._Modulation

    @Modulation.setter
    def Modulation(self, mod: Literal["qpsk", "qam16", "qam64", "qam256"]) -> None:
        assert mod in ["qpsk", "qam16", "qam64", "qam256"], "The value must be in ['qpsk', 'qam16', 'qam64', 'qam256']"
        self._Modulation = mod

    @property
    def NumLayers(self) -> int:
        return self._NumLayers

    @NumLayers.setter
    def NumLayers(self, N: int) -> None:
        assert N in list(range(1, 9)), "The value must be 1..8"
        self._NumLayers = N

    @property
    def ReservedPRB(self) -> None:
        raise NotImplementedError("not ready yet")
        return self._ReservedPRB

    @ReservedPRB.setter
    def ReservedPRB(self, N: int) -> None:
        raise NotImplementedError("not ready yet")
        self._ReservedPRB = None

    @property
    def VRBToPRBInterleaving(self) -> int:
        raise NotImplementedError("not ready yet")
        return self._VRBToPRBInterleaving

    @VRBToPRBInterleaving.setter
    def VRBToPRBInterleaving(self, N: int) -> None:
        raise NotImplementedError("not ready yet")
        assert N in [0, 1], "The value must be 0 or 1"
        self._VRBToPRBInterleaving = 0

    @property
    def VRBBundleSize(self) -> int:
        raise NotImplementedError("not ready yet")
        return self._VRBBundleSize

    @VRBBundleSize.setter
    def VRBBundleSize(self, N: int) -> None:
        raise NotImplementedError("not ready yet")
        assert N in [2, 4], "The value must be 2 or 4"
        self._VRBBundleSize = 0
