from __future__ import annotations

from .PDSCHPTRSConfigBase import PDSCHPTRSConfigBase


class nrPDSCHPTRSConfig(PDSCHPTRSConfigBase):
    def __init__(self) -> None:
        super().__init__()
        self._PTRSPortSet: list = []

    @property
    def PTRSPortSet(self) -> list:
        raise NotImplementedError("not ready yet")
        return self._PTRSPortSet

    @PTRSPortSet.setter
    def PTRSPortSet(self, size: list) -> None:
        raise NotImplementedError("not ready yet")
        self._PTRSPortSet = size
