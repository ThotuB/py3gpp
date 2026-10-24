from __future__ import annotations

from .CommonConfig import CommonConfig
from .PDSCHConfigBase import PDSCHConfigBase


class nrPDSCHConfig(PDSCHConfigBase, CommonConfig):
    def __init__(self) -> None:
        PDSCHConfigBase.__init__(self)
        CommonConfig.__init__(self)
        self._Nid: int = 0
        self._NSizeBWP: int | list = []
        self._NStartBWP: int | list = []

    @property
    def NRBSize(self) -> int:
        return 12

    @property
    def Nid(self) -> int:
        return self._Nid

    @Nid.setter
    def Nid(self, nid: int) -> None:
        assert nid >= 0 and nid <= 1007, "The value must be in the range 0..1007."
        self._Nid = nid

    @property
    def NSizeBWP(self) -> int | list:
        return self._NSizeBWP

    @NSizeBWP.setter
    def NSizeBWP(self, size: int) -> None:
        assert size > 1 and size < 275, "The value must be in the range 1...275."
        self._NSizeBWP = size

    @property
    def NStartBWP(self) -> int | list:
        return self._NStartBWP

    @NStartBWP.setter
    def NStartBWP(self, start: int) -> None:
        assert start >= 0 and start < 2473, "The value must be in the range 0...2473."
        self._NStartBWP = start
