from __future__ import annotations


class DMRSConfigBase:
    def __init__(self) -> None:
        self._NLayers: int = 1
        self._Ports: None = None
        self._DMRSTypeAPosition: int = 2
        self._DMRSAdditionalPosition: int = 0
        self._DMRSLength: int = 1
        self._CustomSymbolSet: list = []
        self._DMRSPortSet: list = []
        self._NIDNSCID: int | list = []
        self._NSCID: int = 0

    @property
    def NLayers(self) -> int:
        return self._NLayers

    @NLayers.setter
    def NLayers(self, N: int) -> None:
        assert N > 0
        self._NLayers = N

    @property
    def Ports(self) -> None:
        return self._Ports

    @property
    def DMRSTypeAPosition(self) -> int:
        return self._DMRSTypeAPosition

    @DMRSTypeAPosition.setter
    def DMRSTypeAPosition(self, pos: int) -> None:
        assert pos in [2, 3]
        self._DMRSTypeAPosition = pos

    @property
    def DMRSAdditionalPosition(self) -> int:
        return self._DMRSAdditionalPosition

    @DMRSAdditionalPosition.setter
    def DMRSAdditionalPosition(self, pos: int) -> None:
        assert pos in list(range(4))
        self._DMRSAdditionalPosition = pos

    @property
    def DMRSLength(self) -> int:
        return self._DMRSLength

    @DMRSLength.setter
    def DMRSLength(self, pos: int) -> None:
        assert pos in list(range(4))
        self._DMRSLength = pos

    @property
    def CustomSymbolSet(self) -> list:
        raise NotImplementedError("not ready yet")
        return self._CustomSymbolSet

    @CustomSymbolSet.setter
    def CustomSymbolSet(self, set: list) -> None:
        raise NotImplementedError("not ready yet")
        self._CustomSymbolSet = set

    @property
    def DMRSPortSet(self) -> list:
        raise NotImplementedError("not ready yet")
        return self._DMRSPortSet

    @DMRSPortSet.setter
    def DMRSPortSet(self, set: list) -> None:
        raise NotImplementedError("not ready yet")
        self._DMRSPortSet = set

    @property
    def NIDNSCID(self) -> int | list:
        return self._NIDNSCID

    @NIDNSCID.setter
    def NIDNSCID(self, nid: int) -> None:
        assert nid >= 0 and nid <= 65535, "The value must be 0..65535"
        self._NIDNSCID = nid

    @property
    def NSCID(self) -> int:
        return self._NSCID

    @NSCID.setter
    def NSCID(self, nscid: int) -> None:
        assert nscid in [0, 1], "The value must be 0 or 1"
        self._NSCID = nscid
