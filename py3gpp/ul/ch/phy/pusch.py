from __future__ import annotations

from typing import Literal, Sequence

import numpy as np
from numpy.typing import NDArray

from py3gpp.dl.ofdm import nrCarrierConfig
from py3gpp.plc.sym import nrPRBS, nrSymbolDemodulate, nrSymbolModulate, nrTransformDeprecode, nrTransformPrecode
from py3gpp.ul.sig.pusch_dmrs import PUSCHDMRSSyms


class CommonConfig:
    def __init__(self) -> None:
        self._MappingType: Literal["A", "B"] = "A"
        self._SymbolAllocation: list[int] = [0, 14]
        self._PRBSet: list[int] = list(range(0, 52))
        self._RNTI: int = 1

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


class DMRSConfigBase:
    def __init__(self) -> None:
        self._DMRSTypeAPosition: int = 2
        self._DMRSAdditionalPosition: int = 0
        self._DMRSLength: int = 1
        self._NIDNSCID: int | None = None
        self._NSCID: int = 0

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
    def NIDNSCID(self) -> int | None:
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


class nrPUSCHDMRSConfig(DMRSConfigBase):
    """PUSCH DM-RS configuration parameters."""

    def __init__(self) -> None:
        super().__init__()
        self._DMRSConfigurationType: Literal[1] = 1

    @property
    def DMRSConfigurationType(self) -> Literal[1]:
        return self._DMRSConfigurationType

    @DMRSConfigurationType.setter
    def DMRSConfigurationType(self, size: Literal[1]) -> None:
        assert size == 1, "DMRSConfigurationType=2 is not yet implemented"
        self._DMRSConfigurationType = size


class PUSCHConfigBase:
    def __init__(self) -> None:
        self._Modulation: Literal["pi/2-bpsk", "qpsk", "qam16", "qam64", "qam256"] = "qpsk"
        self._NumLayers: int = 1
        self._TransformPrecoding: Literal["enabled", "disabled"] = "disabled"

        self.DMRS: nrPUSCHDMRSConfig = nrPUSCHDMRSConfig()

    @property
    def Modulation(self) -> Literal["pi/2-bpsk", "qpsk", "qam16", "qam64", "qam256"]:
        return self._Modulation

    @Modulation.setter
    def Modulation(self, mod: Literal["pi/2-bpsk", "qpsk", "qam16", "qam64", "qam256"]) -> None:
        assert mod in [
            "pi/2-bpsk",
            "qpsk",
            "qam16",
            "qam64",
            "qam256",
        ], "The value must be in ['pi/2-bpsk', 'qpsk', 'qam16', 'qam64', 'qam256']"
        self._Modulation = mod

    @property
    def NumLayers(self) -> int:
        return self._NumLayers

    @NumLayers.setter
    def NumLayers(self, N: int) -> None:
        assert N in list(range(1, 5)), "The value must be 1..4"
        self._NumLayers = N

    @property
    def TransformPrecoding(self) -> Literal["enabled", "disabled"]:
        return self._TransformPrecoding

    @TransformPrecoding.setter
    def TransformPrecoding(self, value: Literal["enabled", "disabled"]) -> None:
        assert value in ["enabled", "disabled"], "The value must be 'enabled' or 'disabled'"
        self._TransformPrecoding = value


class nrPUSCHConfig(PUSCHConfigBase, CommonConfig):
    """PUSCH configuration parameters."""

    def __init__(self) -> None:
        PUSCHConfigBase.__init__(self)
        CommonConfig.__init__(self)
        self._Nid: int = 0
        self._NSizeBWP: int | None = None
        self._NStartBWP: int | None = None

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
    def NSizeBWP(self) -> int | None:
        return self._NSizeBWP

    @NSizeBWP.setter
    def NSizeBWP(self, size: int) -> None:
        assert size > 1 and size < 275, "The value must be in the range 1...275."
        self._NSizeBWP = size

    @property
    def NStartBWP(self) -> int | None:
        return self._NStartBWP

    @NStartBWP.setter
    def NStartBWP(self, start: int) -> None:
        assert start >= 0 and start < 2473, "The value must be in the range 0...2473."
        self._NStartBWP = start


def nrPUSCHPRBS(rnti: int, nid: int, length: int) -> NDArray[np.int32]:
    """Generate PUSCH scrambling sequence."""
    # TS 38.211 6.3.1.1: unlike PDSCH, PUSCH never carries 2 codewords, so there's no codeword-index term
    cinit = (rnti * 2**15 + nid) % 2**31
    return nrPRBS(cinit, length)


def nrPUSCH(
    cw: NDArray[np.int_],
    modulation: str,
    nlayers: int,
    nid: int,
    rnti: int,
    mrb: int = 0,
    transform_precoding: Literal["enabled", "disabled"] = "disabled",
) -> NDArray[np.complex128]:
    """Generate PUSCH modulation symbols."""
    if nlayers != 1:
        raise NotImplementedError("not ready yet")

    scrambling_seq = nrPUSCHPRBS(rnti, nid, len(cw))
    scrambled_bits = np.bitwise_xor(cw, scrambling_seq)
    syms = nrSymbolModulate(scrambled_bits, modulation)

    if transform_precoding == "enabled":
        assert mrb > 0, "mrb (number of allocated PRBs) is required when TransformPrecoding is 'enabled'"
        syms = nrTransformPrecode(syms, mrb)

    return np.array([syms])


def nrPUSCHDecode(
    sym: NDArray[np.complex128],
    mod: Literal["BPSK", "QPSK", "16QAM", "64QAM", "256QAM"],
    nid: int,
    rnti: int,
    mrb: int = 0,
    transform_precoding: Literal["enabled", "disabled"] = "disabled",
) -> NDArray[np.float64]:
    """Decode PUSCH modulation symbols."""
    n_layers = sym.shape[0]
    if n_layers != 1:
        raise NotImplementedError("not ready yet")

    syms = sym[0]
    if transform_precoding == "enabled":
        assert mrb > 0, "mrb (number of allocated PRBs) is required when TransformPrecoding is 'enabled'"
        syms = nrTransformDeprecode(syms, mrb)

    demod_sym = nrSymbolDemodulate(syms, mod)
    scrambling_seq = nrPUSCHPRBS(rnti, nid, len(demod_sym))
    descrambled_bits = np.multiply(demod_sym, (-scrambling_seq * 2 + 1))
    return np.array([descrambled_bits])


def nrPUSCHIndices(carrier: nrCarrierConfig, pusch: nrPUSCHConfig) -> NDArray[np.int_]:
    """Generate PUSCH resource element indices."""
    NStartBWP = carrier.NStartGrid if pusch.NStartBWP is None else pusch.NStartBWP

    frame_begin = pusch.NRBSize * (min(pusch.PRBSet))
    frame_end = pusch.NRBSize * (max(pusch.PRBSet) + 1)

    occupied_syms = np.arange(pusch.SymbolAllocation[0], pusch.SymbolAllocation[1])
    indices = np.repeat(np.expand_dims(np.arange(frame_begin, frame_end), 0), occupied_syms.shape[0], axis=0)
    for i in range(indices.shape[0]):
        indices[i, :] += carrier.NSizeGrid * pusch.NRBSize * i + NStartBWP * pusch.NRBSize
    indices = np.delete(indices, PUSCHDMRSSyms(pusch), axis=0)
    return indices.ravel()
