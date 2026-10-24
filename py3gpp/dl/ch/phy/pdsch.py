from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from py3gpp.dl.ofdm import nrCarrierConfig
from py3gpp.dl.sig.pdsch_dmrs import PDSCHDMRSSyms
from py3gpp.plc.sym import nrPRBS, nrSymbolDemodulate, nrSymbolModulate


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


class nrPDSCHDMRSConfig(DMRSConfigBase):
    def __init__(self) -> None:
        super().__init__()
        self._DMRSConfigurationType: Literal[1, 2] = 1
        self._DMRSReferencePoint: Literal["CRB0", "PRB0"] = "CRB0"
        self._NumCDMGroupsWithoutData: int = 2
        self._DMRSDownlinkR16: int = 0

    @property
    def DMRSConfigurationType(self) -> Literal[1, 2]:
        return self._DMRSConfigurationType

    @DMRSConfigurationType.setter
    def DMRSConfigurationType(self, size: Literal[1, 2]) -> None:
        assert size in [1, 2], "The value must be 1 or 2."
        self._DMRSConfigurationType = size

    @property
    def DMRSReferencePoint(self) -> Literal["CRB0", "PRB0"]:
        raise NotImplementedError("not ready yet")
        return self._DMRSReferencePoint

    @DMRSReferencePoint.setter
    def DMRSReferencePoint(self, size: Literal["CRB0", "PRB0"]) -> None:
        raise NotImplementedError("not ready yet")
        assert size in ["CRB0", "PRB0"], "The value must be 'CRB0' or 'PRB0'."
        self._DMRSReferencePoint = size

    @property
    def NumCDMGroupsWithoutData(self) -> int:
        raise NotImplementedError("not ready yet")
        return self._NumCDMGroupsWithoutData

    @NumCDMGroupsWithoutData.setter
    def NumCDMGroupsWithoutData(self, N: int) -> None:
        raise NotImplementedError("not ready yet")
        assert N in [1, 2, 3], "The value must be 1, 2 or 3."
        self._NumCDMGroupsWithoutData = N

    @property
    def DMRSDownlinkR16(self) -> int:
        raise NotImplementedError("not ready yet")
        return self._DMRSDownlinkR16

    @DMRSDownlinkR16.setter
    def DMRSDownlinkR16(self, N: int) -> None:
        raise NotImplementedError("not ready yet")
        self._DMRSDownlinkR16 = N


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


def nrPDSCH(
    cws: list[NDArray[np.int_]], modulation: list[str], nlayers: int, nid: int, nrnti: int
) -> NDArray[np.complex128]:
    if nlayers != 1:
        raise NotImplementedError("not ready yet")
    assert nlayers in list(range(1, 9))

    if nlayers > 4:
        ncw = 2
    else:
        ncw = 1

    scrambled_bits = []
    res_sym = []
    for i in range(ncw):
        databits = cws[i]
        cinit = (nrnti * 2**15) + (i * 2**14) + nid
        prbs_bits = nrPRBS(cinit, len(databits))
        scrambled_bits.append(np.bitwise_xor(databits, prbs_bits))
        scrambled_bits = np.array(scrambled_bits)

        res_sym.append(nrSymbolModulate(scrambled_bits[i], modulation[i]))

    # TODO
    # res_sym = nrLayerMap(res_sym, nlayers)
    # res_sym = np.hstack(res_sym)

    return np.array(res_sym)


def nrPDSCHDecode(sym: NDArray[np.complex128], mod: list[str], nid: int, rnti: int) -> NDArray[np.float64]:
    descrambled_bits = []
    n_layers = sym.shape[0]
    if n_layers != 1:
        raise NotImplementedError("not ready yet")

    for i in range(n_layers):
        demod_sym = nrSymbolDemodulate(sym[i], mod[i])
        cinit = (rnti * 2**15) + (i * 2**14) + nid
        prbs_bits = nrPRBS(cinit, len(demod_sym))
        descrambled_bits.append(np.multiply(demod_sym, (-prbs_bits * 2 + 1)))
        descrambled_bits = np.array(descrambled_bits)
    return descrambled_bits


def nrPDSCHIndices(carrier: nrCarrierConfig, pdsch: nrPDSCHConfig) -> NDArray[np.int_]:
    frame_begin = pdsch.NRBSize * (min(pdsch.PRBSet))
    frame_end = pdsch.NRBSize * (max(pdsch.PRBSet) + 1)

    occupied_syms = np.arange(pdsch.SymbolAllocation[0], pdsch.SymbolAllocation[1])
    indices = np.repeat(np.expand_dims(np.arange(frame_begin, frame_end), 0), occupied_syms.shape[0], axis=0)
    for i in range(indices.shape[0]):
        indices[i, :] += carrier.NSizeGrid * pdsch.NRBSize * i + pdsch.NStartBWP * pdsch.NRBSize
    indices = np.delete(indices, PDSCHDMRSSyms(pdsch), axis=0)
    return indices.ravel()


if __name__ == "__main__":
    modulation = ["16QAM"]
    nlayers = 1
    ncellid = 42
    rnti = 6143
    data = np.random.randint(0, 2, size=(1, 8000))

    txsym = nrPDSCH(data, modulation, nlayers, ncellid, rnti)
    rxbits = nrPDSCHDecode(txsym, modulation, ncellid, rnti)
    assert np.array_equal(data, np.round(rxbits < 0).astype(int))

    pdsch_cfg = nrPDSCHConfig()
    carrier_cfg = nrCarrierConfig()
    carrier_cfg.NSizeGrid = 52
    pdsch_cfg.NSizeBWP = 25
    pdsch_cfg.NStartBWP = 10
    pdsch_cfg.PRBSet = np.arange(pdsch_cfg.NSizeBWP)
    indices = nrPDSCHIndices(carrier_cfg, pdsch_cfg)
    print(indices.shape)
    print(indices)
