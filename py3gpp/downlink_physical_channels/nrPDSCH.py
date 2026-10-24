from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from py3gpp.physical_channel_and_signal_subcomponents.nrPRBS import nrPRBS
from py3gpp.physical_channel_and_signal_subcomponents.nrSymbolModulate import nrSymbolModulate


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
