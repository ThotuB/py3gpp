from __future__ import annotations

from typing import Any, Literal

import numpy as np
import scipy
from numpy.typing import NDArray

from py3gpp import nrOFDMModulate
from py3gpp.configs.nrCarrierConfig import nrCarrierConfig


def nrTimingEstimate(
    carrier: nrCarrierConfig | None = None,
    waveform: NDArray[np.complex128] | None = None,
    refGrid: NDArray[Any] | None = None,
    nrb: int | None = None,
    scs: int | None = None,
    initialNSlot: int | None = None,
    refInd: NDArray[np.int_] | None = None,
    refSym: NDArray[np.complex128] | None = None,
    CyclicPrefix: Literal["normal", "extended"] = "normal",
    Nfft: int | None = None,
    SampleRate: float | None = None,
    CarrierFrequency: float = 0,
) -> int:
    refWaveform, _ = nrOFDMModulate(
        grid=refGrid,
        scs=scs,
        initialNSlot=initialNSlot,
        SampleRate=SampleRate,
        Nfft=Nfft,
        carrier=carrier,
        CarrierFrequency=CarrierFrequency,
    )
    xcorr = scipy.signal.correlate(waveform, refWaveform, "valid")
    index = np.argmax(np.abs(xcorr))
    return index
