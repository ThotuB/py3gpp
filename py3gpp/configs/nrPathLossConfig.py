# Ref: https://www.mathworks.com/help/5g/ref/nrpathlossconfig.html
from __future__ import annotations

from typing import Literal

Scenario = Literal["UMa", "UMi", "RMa", "InH", "InF-SL", "InF-DL", "InF-SH", "InF-DH", "InF-HH"]


class nrPathLossConfig:
    def __init__(self) -> None:
        self._Scenario: Scenario = "UMa"
        self._BuildingHeight: int = 5
        self._StreetWidth: int = 20
        self._EnvironmentHeight: int = 1
        self._OptionalModel: int | bool = 0

    @property
    def Scenario(self) -> Scenario:
        return self._Scenario

    @Scenario.setter
    def Scenario(self, Scenario: Scenario) -> None:
        assert Scenario in [
            "UMa",
            "UMi",
            "RMa",
            "InH",
            "InF-SL",
            "InF-DL",
            "InF-SH",
            "InF-DH",
            "InF-HH",
        ], "The value must be in 'UMa', 'UMi', 'RMa', 'InH', 'InF-SL', 'InF-DL', 'InF-SH', 'InF-DH', or 'InF-HH'"
        self._Scenario = Scenario

    @property
    def BuildingHeight(self) -> int:
        return self._BuildingHeight

    @BuildingHeight.setter
    def BuildingHeight(self, BuildingHeight: int) -> None:
        assert BuildingHeight >= 5 and BuildingHeight <= 50, "The value must be 5..50"
        self._BuildingHeight = BuildingHeight

    @property
    def StreetWidth(self) -> int:
        return self._StreetWidth

    @StreetWidth.setter
    def StreetWidth(self, StreetWidth: int) -> None:
        assert StreetWidth >= 5 and StreetWidth <= 50, "The value must be 5..50"
        self._StreetWidth = StreetWidth

    @property
    def EnvironmentHeight(self) -> int:
        return self._EnvironmentHeight

    @EnvironmentHeight.setter
    def EnvironmentHeight(self, EnvironmentHeight: int) -> None:
        self._EnvironmentHeight = EnvironmentHeight

    @property
    def OptionalModel(self) -> int | bool:
        return self._OptionalModel

    @OptionalModel.setter
    def OptionalModel(self, OptionalModel: int | bool) -> None:
        assert OptionalModel in [0, 1, True, False], "The value must be 0 / False or 1 / True"
        self._OptionalModel = OptionalModel


# # Example usage
# pathlossconf = nrPathLossConfig()
# print(f'Scenario: ', pathlossconf.Scenario)
# print(f'BuildingHeight: ', pathlossconf.BuildingHeight)
# print(f'StreetWidth: ', pathlossconf.StreetWidth)
# print(f'EnvironmentHeight: ', pathlossconf.EnvironmentHeight)
# print(f'OptionalModel: ', pathlossconf.OptionalModel)
