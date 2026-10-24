from __future__ import annotations

from typing import Any, Literal

import numpy as np
import scipy
from numpy.typing import NDArray

from py3gpp.dl.ofdm import nrCarrierConfig, nrOFDMModulate, nrSetResources

Scenario = Literal["UMa", "UMi", "RMa", "InH", "InF-SL", "InF-DL", "InF-SH", "InF-DH", "InF-HH"]


class nrPathLossConfig:
    """Path loss configuration parameters."""

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


def nrChannelEstimate(
    rxGrid: NDArray[np.complexfloating] | None = None,
    refInd: NDArray[np.int_] | None = None,
    refSym: NDArray[np.complexfloating] | None = None,
    refGrid: NDArray[np.complexfloating] | None = None,
    carrier: nrCarrierConfig | None = None,
) -> tuple[NDArray[np.complexfloating], float] | None:
    """Practical channel estimation."""
    assert rxGrid is not None, "rxGrid is required"
    cp = "normal" if carrier is None else "extended"
    if refGrid is None:
        if (refInd is None) or (refSym is None):
            print("Error: refInd and refSym need to be given when refGrid is None!")
            return
        refGrid = np.zeros(rxGrid.shape, "complex")
        nrSetResources(refInd, refGrid, refSym)
    else:
        pilot_idx = np.where(refGrid.ravel(order="F") != 0)
        refInd = pilot_idx[0]
        refSym = refGrid.ravel(order="F")[refInd]

    rxSym = rxGrid.ravel(order="F")[refInd]
    L = 14 if cp == "normal" else 12
    K = rxGrid.shape[0]  # number of subcarriers
    N = rxGrid.shape[1]  # number of symbols
    H = np.zeros(refGrid.shape, "complex")
    R, C = np.mgrid[:K, :N]
    normGrid = rxGrid / refGrid
    idx_nonzero = np.where(np.invert(np.isinf(normGrid.ravel(order="F"))))[0]
    normXYZ = np.column_stack(
        (C.ravel(order="F")[idx_nonzero], R.ravel(order="F")[idx_nonzero], normGrid.ravel(order="F")[idx_nonzero])
    )

    if True:
        # this one works best!
        interp_vertical = False
        for col in range(N):
            idx = np.where(np.logical_and(refInd >= col * K, refInd < (col + 1) * K))[0]
            if len(idx) > 0:
                sym_idx = refInd[idx] - col * K
                H[:, col] = np.interp(np.arange(K), sym_idx, rxSym[idx] / refSym[idx])
            else:
                interp_vertical = True
        if interp_vertical:
            for row in range(K):
                temp = H[row, :]
                idx = np.where(temp != 0)[0]
                H[row, :] = np.interp(np.arange(N), idx, temp[idx])

        # estimate noise variance
        mean = np.mean((np.abs(H[:, 1]), np.abs(H[:, 3])), axis=0)
        nVar = np.mean(np.abs(np.abs(H[:, 1]) - mean))

    elif False:
        H = scipy.interpolate.griddata(
            (normXYZ[:, 0].real, normXYZ[:, 1].real), normXYZ[:, 2], (C.ravel(order="F"), R.ravel(order="F"))
        ).reshape(refGrid.shape, order="F")
    elif False:
        # use RBFInterpolator because interp2d and griddata cannot extrapolate
        interpolator = scipy.interpolate.RBFInterpolator(
            np.array((normXYZ[:, 0].real, normXYZ[:, 1].real)).T, normXYZ[:, 2]
        )
        H = interpolator(np.vstack((C.ravel(order="F"), R.ravel(order="F"))).T).reshape(refGrid.shape, order="F")
    return H, nVar


def nrTimingEstimate(
    carrier: nrCarrierConfig | None = None,
    waveform: NDArray[np.complex128] | None = None,
    refGrid: NDArray[Any] | None = None,
    nrb: int | None = None,
    scs: Literal[15, 30, 60, 120, 240] | None = None,
    initialNSlot: int | None = None,
    refInd: NDArray[np.int_] | None = None,
    refSym: NDArray[np.complex128] | None = None,
    CyclicPrefix: Literal["normal", "extended"] = "normal",
    Nfft: int | None = None,
    SampleRate: int | None = None,
    CarrierFrequency: float = 0,
) -> int:
    """Practical timing estimation."""
    assert refGrid is not None, "refGrid is required"
    modulated = nrOFDMModulate(
        grid=refGrid,
        scs=scs,
        initialNSlot=initialNSlot,
        SampleRate=SampleRate,
        Nfft=Nfft,
        carrier=carrier,
        CarrierFrequency=CarrierFrequency,
    )
    assert modulated is not None
    refWaveform, _ = modulated
    xcorr = scipy.signal.correlate(waveform, refWaveform, "valid")
    index = np.argmax(np.abs(xcorr))
    return int(index)


def nrEqualizeMMSE(
    rxSym: NDArray[np.complexfloating], hest: NDArray[np.complexfloating], nVar: float
) -> tuple[NDArray[np.complexfloating], NDArray[np.floating]]:
    """Minimum mean-squared error (MMSE) equalization."""
    csi = np.abs(hest * np.conj(hest)) + nVar
    # rxEq = rxSym / hest # zero forcing
    rxEq = rxSym * np.conj(hest) / csi
    return rxEq, csi


def nrExtractResources(ind: NDArray[np.int_], grid: NDArray[Any]) -> NDArray[Any]:
    """Extract resource elements from resource array."""
    return grid.ravel(order="F")[ind]


# Ref: https://www.mathworks.com/help/5g/ref/nrpathloss.html#d124e18391
# Ref: TR 38.901 Section 7.4.1
def nrPathLoss(
    pathlossconf: nrPathLossConfig,
    freq: int | float,
    los: bool | int | NDArray[np.bool_],
    bs: NDArray[np.floating],
    ue: NDArray[np.floating],
) -> tuple[float, float]:
    """Path loss and shadow fading between BS and UE."""

    # Check the input types
    if not isinstance(freq, (int, float)):
        raise TypeError("freq must be a positive numeric scalar")

    if not isinstance(los, (bool, int, np.ndarray)):
        raise TypeError("los must be true, false, 1, 0, or a logical matrix")

    if not isinstance(bs, np.ndarray) or not isinstance(ue, np.ndarray):
        raise TypeError("bs and ue must be numeric matrices")

    # Path loss equation
    if pathlossconf.Scenario == "RMa":

        if not isinstance(los, (bool, int)):
            # TODO multi bs-ue link
            raise TypeError("multi bs-ue link not yet supported.")

        else:
            c = 3e8  # Speed of light (m/s)
            dist_bp = 2 * np.pi * bs[2] * ue[2] * (freq / c)
            dist_2d = np.sqrt((ue[0] - bs[0]) ** 2 + (ue[1] - bs[1]) ** 2)
            dist_3d = np.sqrt((dist_2d) ** 2 + (bs[2] - ue[2]) ** 2)

            pathloss_one = 0
            pathloss_two = 0
            shadowfading_one = 0
            shadowfading_two = 0

            pathloss_one += 20 * np.log10(40 * np.pi * dist_3d * (freq / 1e9) / 3)
            pathloss_one += min((0.03 * (pathlossconf.BuildingHeight**1.72)), 10) * np.log10(dist_3d)
            pathloss_one += -min((0.044 * (pathlossconf.BuildingHeight**1.72)), 14.77)
            pathloss_one += 0.002 * np.log10(pathlossconf.BuildingHeight) * dist_3d

            if dist_2d <= dist_bp:
                shadowfading_one = 4
                pathloss_los = pathloss_one
                shadowfading_los = shadowfading_one

            else:
                pathloss_two += 10 * np.log10((10 ** (pathloss_one / 10)) * dist_bp)
                pathloss_two += 40 * np.log10(dist_3d / dist_bp)
                shadowfading_two = 6
                pathloss_los = pathloss_two
                shadowfading_los = shadowfading_two

            if los in [True, 1]:  # LOS case

                pathloss = pathloss_los
                shadowfading = shadowfading_los

            elif los in [False, 0]:  # NLOS case

                pathloss_nlos_ = 0
                pathloss_nlos_ += 161.04
                pathloss_nlos_ += -(7.1 * np.log10(pathlossconf.StreetWidth))
                pathloss_nlos_ += 7.5 * np.log10(pathlossconf.BuildingHeight)
                pathloss_nlos_ += -(24.37 - (3.7 * (pathlossconf.BuildingHeight / bs[2]) ** 2)) * np.log10(bs[2])
                pathloss_nlos_ += (43.42 - (3.1 * np.log10(bs[2]))) * ((np.log10(dist_3d)) - 3)
                pathloss_nlos_ += (20 * np.log10(freq / 1e9)) - (3.2 * (np.log10(11.75 * ue[2]))) ** 2 - 4.97

                shadowfading_nlos = 8

                pathloss_nlos = max(pathloss_los, pathloss_nlos_)

                pathloss = pathloss_nlos
                shadowfading = shadowfading_nlos

            else:

                raise TypeError("los for single bs-ue link must be true, false, 1, 0")

    else:

        raise TypeError("This path loss model is not yet supported.")

    return pathloss, shadowfading


# # Example usage
# pathlossconf = nrPathLossConfig()
# pathlossconf.Scenario = "RMa"
# pathlossconf.BuildingHeight = 7
# pathlossconf.StreetWidth = 25
# freq = 3.5e9
# los = True
# bs = np.array([0, 0, 30])
# ue = np.array([1000, 1000, 1.5])
# pathloss, shadowfading = nrPathLoss(pathlossconf, freq, los, bs, ue)
# print("Path Loss:", pathloss)
# print("Shadow Fading:", shadowfading)
