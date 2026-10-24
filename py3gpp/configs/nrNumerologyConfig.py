from __future__ import annotations

from typing import Literal


class nrNumerologyConfig:
    def __init__(self) -> None:
        self._SubcarrierSpacing: Literal[15, 30, 60, 120, 240] = 15
        self._CyclicPrefix: Literal["normal", "extended"] = "normal"

    @property
    def SubcarrierSpacing(self) -> Literal[15, 30, 60, 120, 240]:
        return self._SubcarrierSpacing

    @SubcarrierSpacing.setter
    def SubcarrierSpacing(self, spacing: Literal[15, 30, 60, 120, 240]) -> None:
        assert spacing in [15, 30, 60, 120, 240], "The value must be [15, 30, 60, 120, 240]"
        self._SubcarrierSpacing = spacing

    @property
    def CyclicPrefix(self) -> Literal["normal", "extended"]:
        return self._CyclicPrefix

    @CyclicPrefix.setter
    def CyclicPrefix(self, pref: Literal["normal", "extended"]) -> None:
        assert pref in ["normal", "extended"], "The value must be in ['extended' or 'normal'']"
        self._CyclicPrefix = pref
