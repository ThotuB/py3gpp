from __future__ import annotations

from typing import Literal


class CommonConfig:
    def __init__(self) -> None:
        self._MappingType: Literal["A", "B"] = "A"
        self._SymbolAllocation: list[int] = [0, 14]
        self._PRBSet: list[int] = list(range(0, 52))
        self._RNTI: int = 1
        self._EnablePTRS: Literal[0, 1] = 0

    @property
    def MappingType(self) -> Literal["A", "B"]:
        return self._MappingType

    @MappingType.setter
    def MappingType(self, map_type: Literal["A", "B"]) -> None:
        assert map_type in ["A", "B"], "The value must be in A or B"
        self._MappingType = map_type

    @property
    def SymbolAllocation(self) -> list[int]:
        return self._SymbolAllocation

    @SymbolAllocation.setter
    def SymbolAllocation(self, sym_list: list[int]) -> None:
        # assert prbset > 0 and prbset < self._n_size_bwp, "The value must be 0..n_size_bwp"
        self._SymbolAllocation = sym_list

    @property
    def PRBSet(self) -> list[int]:
        return self._PRBSet

    @PRBSet.setter
    def PRBSet(self, prbset: list[int]) -> None:
        assert min(prbset) >= 0 and max(prbset) <= 274, "The value must be 0..274"
        self._PRBSet = prbset

    @property
    def RNTI(self) -> int:
        return self._RNTI

    @RNTI.setter
    def RNTI(self, rnti: int) -> None:
        assert rnti >= 0 and rnti <= 65535, "The value must be 0..65535"
        self._RNTI = rnti

    @property
    def EnablePTRS(self) -> Literal[0, 1]:
        return self._EnablePTRS

    @EnablePTRS.setter
    def EnablePTRS(self, enable: Literal[0, 1]) -> None:
        assert enable in [0, 1], "The value must be 0 or 1"
        self._EnablePTRS = enable
