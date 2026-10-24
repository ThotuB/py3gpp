from __future__ import annotations

from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray


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


class nrCarrierConfig(nrNumerologyConfig):
    """Carrier configuration parameters."""

    def __init__(
        self,
        NCellID: int = 1,
        NSizeGrid: int = 52,
        NStartGrid: int = 0,
        NSlot: int = 0,
        NFrame: int = 0,
        SubcarrierSpacing: int = 15,
    ) -> None:
        super().__init__()
        self._NCellID = NCellID
        self._NSizeGrid = NSizeGrid
        self._NStartGrid = NStartGrid
        self._NSlot = NSlot
        self._NFrame = NFrame
        self.SubcarrierSpacing = SubcarrierSpacing

    @property
    def SymbolsPerSlot(self) -> int:
        if self.CyclicPrefix == "normal":
            return 14
        else:
            return 12

    @property
    def SlotsPerSubframe(self) -> int:
        return self.SubcarrierSpacing // 15

    @property
    def SlotsPerFrame(self) -> int:
        return int(10 * (self.SubcarrierSpacing / 15))

    @property
    def NCellID(self) -> int:
        return self._NCellID

    @NCellID.setter
    def NCellID(self, nid: int) -> None:
        assert nid >= 0 and nid <= 1007, "The value must be in the range 0...1007."
        self._NCellID = nid

    @property
    def NSizeGrid(self) -> int:
        return self._NSizeGrid

    @NSizeGrid.setter
    def NSizeGrid(self, size: int) -> None:
        assert size > 0 and size <= 275, "The value must be in the range 1...275."
        self._NSizeGrid = size

    @property
    def NStartGrid(self) -> int:
        return self._NStartGrid

    @NStartGrid.setter
    def NStartGrid(self, start: int) -> None:
        assert start >= 0 and start <= 2199, "The value must be in the range 0...2999."
        self._NStartGrid = start

    @property
    def NSlot(self) -> int:
        return self._NSlot

    @NSlot.setter
    def NSlot(self, num: int) -> None:
        assert num >= 0, "The value must be scalar, nonnegative."
        self._NSlot = num

    @property
    def NFrame(self) -> int:
        return self._NFrame

    @NFrame.setter
    def NFrame(self, num: int) -> None:
        assert num >= 0, "The value must be scalar, nonnegative."
        self._NFrame = num


def nrOFDMInfo(
    carrier: nrCarrierConfig | None = None, nrb: int | None = None, scs: int | None = None
) -> dict[str, int] | None:
    """Get OFDM information."""
    if nrb is None or scs is None:
        if carrier is None:
            print("Error: carrier is needed when no nrb or scs is given!")
            return
        nrb = carrier.NSizeGrid
        scs = carrier.SubcarrierSpacing

    for i in range(20):
        if 2 ** (i) * 0.85 >= nrb * 12:
            Nfft = 2**i
            break
    info = dict()
    info["Nfft"] = Nfft
    return info


# TODO: implement windowing
def nrOFDMModulate(
    carrier: nrCarrierConfig | None = None,
    grid: NDArray[np.complexfloating] | None = None,
    scs: int | None = None,
    initialNSlot: int | None = None,
    CyclicPrefix: Literal["normal", "extended"] = "normal",
    Nfft: int | None = None,
    SampleRate: int | None = None,
    Windowing: Any | None = None,
    CarrierFrequency: float = 0,
) -> list | None:
    """Generate OFDM modulated waveform."""
    info = {}

    if carrier is None:
        if grid is None:
            print("Error: grid is needed when no carrierConfig is specified!")
            return
        NSizeGrid = grid.shape[0] // 12
        carrier = nrCarrierConfig(NSizeGrid=NSizeGrid)
        if initialNSlot is None:
            initialNSlot = carrier.NSlot
    else:
        NSizeGrid = carrier.NSizeGrid
        if initialNSlot is None:
            initialNSlot = carrier.NSlot

    if initialNSlot is None:
        initialNSlot = 0

    if scs is None:
        scs = carrier.SubcarrierSpacing

    if Nfft is None:
        if SampleRate is None:
            Nfft = nrOFDMInfo(nrb=NSizeGrid, scs=scs)["Nfft"]
            SampleRate = int(Nfft * scs * 1000)
        else:
            Nfft = int(SampleRate // scs // 1000)

    mu = (scs // 15) - 1

    info["Nfft"] = Nfft
    info["SampleRate"] = SampleRate
    info["CyclicPrefixLengths"] = np.empty(0, "int")
    info["SymbolLengths"] = np.empty(0, "int")
    if len(grid.shape) == 1:
        grid = grid[..., np.newaxis]
    nSlots = grid.shape[1]
    waveform = np.empty(0, "complex")
    if CyclicPrefix == "normal":
        N_cp1 = int(((144) * 2 ** (-mu) + 16) * (SampleRate / 30720000))
        N_cp2 = int((144 * 2 ** (-mu)) * (SampleRate / 30720000))
    else:
        N_cp1 = int((512 * 2 ** (-mu)) * (SampleRate / 30720000))
        N_cp2 = N_cp1
    N_cp = np.zeros(carrier.SymbolsPerSlot, dtype=int)
    for i in range(len(N_cp)):
        N_cp[i] = N_cp1 if i == 0 or i == 7 * 2 ** (mu) else N_cp2

    sample_pos_in_slot = 0
    for i in range(initialNSlot):
        sample_pos_in_slot += Nfft + N_cp[i]

    for sym_pos_in_grid in range(nSlots):
        sym_pos_in_slot = (sym_pos_in_grid + initialNSlot) % carrier.SymbolsPerSlot
        symbol_len = Nfft + N_cp[sym_pos_in_slot]
        nFill = (Nfft - grid.shape[0]) // 2
        if nFill < 0:
            full_slot_grid = grid[np.abs(nFill) :, sym_pos_in_grid][:nFill]
        else:
            full_slot_grid = np.concatenate([np.zeros(nFill), grid[:, sym_pos_in_grid], np.zeros(nFill)])

        # phase compensation according to TS 38.211 section 5.4
        if sym_pos_in_slot == 0:
            sample_pos_in_slot = 0
        sample_pos_in_slot += N_cp[sym_pos_in_slot]
        # print(f'symbol {sym_pos_in_slot}, pos {sample_pos_in_slot}, CP {N_cp[sym_pos_in_slot]}, pos = {len(waveform)}')
        full_slot_grid *= np.exp(-1j * 2 * np.pi * CarrierFrequency / SampleRate * sample_pos_in_slot)
        sample_pos_in_slot += Nfft

        symbol_waveform = np.fft.ifft(np.fft.fftshift(full_slot_grid))
        symbol_waveform_cp = np.append(symbol_waveform[-N_cp[sym_pos_in_slot] :], symbol_waveform)
        waveform = np.append(waveform, symbol_waveform_cp)
        info["CyclicPrefixLengths"] = np.append(info["CyclicPrefixLengths"], N_cp[sym_pos_in_slot])
        info["SymbolLengths"] = np.append(info["SymbolLengths"], symbol_len)
        # print(f'slot {slot_num}, cp_len {N_cp[sym_pos_in_slot]}')
    return [waveform, info]


# TODO: implement CyclicPrefixFraction
def nrOFDMDemodulate(
    carrier: nrCarrierConfig | None = None,
    waveform: NDArray[np.complexfloating] | None = None,
    nrb: int | None = None,
    scs: int | None = None,
    initialNSlot: int | None = None,
    CyclicPrefix: Literal["normal", "extended"] = "normal",
    Nfft: int | None = None,
    SampleRate: int | None = None,
    CarrierFrequency: float = 0,
    CyclicPrefixFraction: float = 0.5,
) -> NDArray[np.complexfloating] | None:
    """Demodulate OFDM waveform."""
    if waveform is None:
        print("Error: no waveform given!")
        return
    if carrier is None:
        if nrb == None:
            print("Error: nrb is needed without carrierConfig!")
            return
        if scs == None:
            print("Error: scs is needed without carrierConfig!")
            return
        if initialNSlot == None:
            print("Error: initialNSlot is needed without carrierConfig!")
            return
        carrier = nrCarrierConfig(1, NSizeGrid=nrb, NStartGrid=0, SubcarrierSpacing=scs, NSlot=initialNSlot)
    else:
        nrb = carrier.NSizeGrid
        scs = carrier.SubcarrierSpacing
        initialNSlot = 0 if initialNSlot is None else initialNSlot

    if Nfft == None:
        if SampleRate == None:
            Nfft = nrOFDMInfo(nrb=nrb, scs=scs)["Nfft"]
            SampleRate = int(Nfft * scs * 1000)
        else:
            Nfft = int(SampleRate // scs // 1000)
    mu = (scs // 15) - 1
    if CyclicPrefix == "normal":
        N_cp1 = int(((144) * 2 ** (-mu) + 16) * (SampleRate / 30720000))
        N_cp2 = int((144 * 2 ** (-mu)) * (SampleRate / 30720000))
    else:
        N_cp1 = int((512 * 2 ** (-mu)) * (SampleRate / 30720000))
        N_cp2 = N_cp1
    N_cp = np.zeros(carrier.SymbolsPerSlot, dtype=int)
    for i in range(len(N_cp)):
        N_cp[i] = N_cp1 if i == 0 or i == 7 * 2 ** (mu) else N_cp2

    idx = 0
    sym_pos_in_slot = initialNSlot
    grid = np.zeros((nrb * 12, 0), "complex")

    sample_pos_in_slot = 0
    for i in range(initialNSlot):
        sample_pos_in_slot += Nfft + N_cp[i]

    symbols_per_slot = carrier.SymbolsPerSlot
    while idx + Nfft <= waveform.shape[0]:
        sym_pos_in_slot = sym_pos_in_slot % symbols_per_slot
        cp_advance = int(CyclicPrefixFraction * N_cp[sym_pos_in_slot])
        idx += cp_advance
        symbol_t = waveform[idx:][:Nfft]
        symbol_f = np.fft.fftshift(np.fft.fft(symbol_t))

        symbol_f *= np.exp(1j * 2 * np.pi * (N_cp[sym_pos_in_slot] - cp_advance) / Nfft * np.arange(len(symbol_f)))
        symbol_f *= np.exp(1j * np.pi * (N_cp[sym_pos_in_slot] - cp_advance))

        symbol_f = symbol_f[Nfft // 2 - nrb * 12 // 2 : Nfft // 2 + nrb * 12 // 2]

        # phase compensation according to TS 38.211 section 5.4
        if sym_pos_in_slot == 0:
            sample_pos_in_slot = 0
        sample_pos_in_slot += N_cp[sym_pos_in_slot]
        # print(f'symbol {sym_pos_in_slot}, pos {sample_pos_in_slot}, CP {N_cp[sym_pos_in_slot]}, pos {idx - cp_advance}')
        symbol_f *= np.exp(1j * 2 * np.pi * CarrierFrequency / SampleRate * sample_pos_in_slot)
        sample_pos_in_slot += Nfft

        grid = np.concatenate((grid, np.expand_dims(symbol_f, 1)), axis=1)
        idx += Nfft + (N_cp[sym_pos_in_slot] - cp_advance)
        # print(f'slot {slot}, cp_len {N_cp}')
        sym_pos_in_slot = sym_pos_in_slot + 1
    return grid


def nrResourceGrid(carrier: nrCarrierConfig, p: int = 1) -> NDArray[np.complex128]:
    """Generate empty carrier slot resource grid."""
    SymbolsPerSlot = 14
    if p == 1:
        grid = np.zeros((12 * carrier.NSizeGrid, SymbolsPerSlot), "complex")
    else:
        grid = np.zeros((12 * carrier.NSizeGrid, SymbolsPerSlot, p), "complex")
    return grid


# this function does not exist in Matlab, but its useful in python because
# numpy does not support integer indexing across dimensions
def nrSetResources(ind: NDArray[np.int_], grid: NDArray[Any], vals: NDArray[Any]) -> NDArray[Any]:
    nSymbols = grid.shape[0]
    for i in range(grid.shape[1]):
        idx = np.where(np.logical_and(ind >= i * nSymbols, ind < (i + 1) * nSymbols))[0]
        if len(idx) != 0:
            grid[ind[idx] - i * nSymbols, i] = vals[idx]
    return vals
