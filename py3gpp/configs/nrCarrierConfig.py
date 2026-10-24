from __future__ import annotations

from .nrNumerologyConfig import nrNumerologyConfig


class nrCarrierConfig(nrNumerologyConfig):
    def __init__(
        self,
        NCellID: int = 1,
        NSizeGrid: int = 52,
        NStartGrid: int = 0,
        NSlot: int = 0,
        NFrame: int = 0,
        SubcarrierSpacing: int = 15,
    ) -> None:
        super().__init__()
        self._NCellID = NCellID
        self._NSizeGrid = NSizeGrid
        self._NStartGrid = NStartGrid
        self._NSlot = NSlot
        self._NFrame = NFrame
        self.SubcarrierSpacing = SubcarrierSpacing

    @property
    def SymbolsPerSlot(self) -> int:
        if self.CyclicPrefix == "normal":
            return 14
        else:
            return 12

    @property
    def SlotsPerSubframe(self) -> int:
        return self.SubcarrierSpacing // 15

    @property
    def SlotsPerFrame(self) -> int:
        return int(10 * (self.SubcarrierSpacing / 15))

    @property
    def NCellID(self) -> int:
        return self._NCellID

    @NCellID.setter
    def NCellID(self, nid: int) -> None:
        assert nid >= 0 and nid <= 1007, "The value must be in the range 0...1007."
        self._NCellID = nid

    @property
    def NSizeGrid(self) -> int:
        return self._NSizeGrid

    @NSizeGrid.setter
    def NSizeGrid(self, size: int) -> None:
        assert size > 0 and size <= 275, "The value must be in the range 1...275."
        self._NSizeGrid = size

    @property
    def NStartGrid(self) -> int:
        return self._NStartGrid

    @NStartGrid.setter
    def NStartGrid(self, start: int) -> None:
        assert start >= 0 and start <= 2199, "The value must be in the range 0...2999."
        self._NStartGrid = start

    @property
    def NSlot(self) -> int:
        return self._NSlot

    @NSlot.setter
    def NSlot(self, num: int) -> None:
        assert num >= 0, "The value must be scalar, nonnegative."
        self._NSlot = num

    @property
    def NFrame(self) -> int:
        return self._NFrame

    @NFrame.setter
    def NFrame(self, num: int) -> None:
        assert num >= 0, "The value must be scalar, nonnegative."
        self._NFrame = num
