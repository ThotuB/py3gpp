from __future__ import annotations

from typing import Literal


class PDSCHPTRSConfigBase:
    def __init__(self) -> None:
        self._TimeDensity: Literal[1, 2, 4] = 1
        self._FrequencyDensity: Literal[2, 4] = 2
        self._REOffset: Literal["00", "01", "10", "11"] = "00"

    @property
    def TimeDensity(self) -> Literal[1, 2, 4]:
        return self._TimeDensity

    @TimeDensity.setter
    def TimeDensity(self, td: Literal[1, 2, 4]) -> None:
        assert td in [1, 2, 4], "The value must be 1, 2 or 4"
        self._TimeDensity = td

    @property
    def FrequencyDensity(self) -> Literal[2, 4]:
        return self._FrequencyDensity

    @FrequencyDensity.setter
    def FrequencyDensity(self, fd: Literal[2, 4]) -> None:
        assert fd in [2, 4], "The value must be 2 or 4"
        self._FrequencyDensity = fd

    @property
    def REOffset(self) -> Literal["00", "01", "10", "11"]:
        return self._REOffset

    @REOffset.setter
    def REOffset(self, offset: Literal["00", "01", "10", "11"]) -> None:
        assert offset in ["00", "01", "10", "11"], "The value must be in ['00', '01', '10', '11']"
        self._REOffset = offset
