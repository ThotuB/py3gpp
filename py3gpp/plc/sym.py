# Ref: https://www.mathworks.com/help/5g/ref/nrlayermap.html
# Ref: TS 38.211 Sections 7.3.1.3
from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from py3gpp.helper import _calc_m_seq


# TS 38.211 Section 5.2.1
def nrPRBS(c_init: int, length: int) -> NDArray[np.int32]:
    """Generate PRBS."""
    assert length > 0

    N = 31

    c_0 = np.zeros(N)
    c_0[0] = 1
    c_1 = np.zeros(N)
    for i in range(N):
        c_1[i] = (c_init >> i) & 1

    Nc = 1600
    seq_len = length + Nc
    mseq_0 = _calc_m_seq(N, c_0, [0, 3], seq_len)
    mseq_1 = _calc_m_seq(N, c_1, [0, 1, 2, 3], seq_len)

    gold_seq = (mseq_0 + mseq_1) % 2
    gold_seq = np.roll(gold_seq, -Nc)
    return gold_seq[:length]


# 38.211 5.1 Modulation mapper
def nrSymbolModulate(databits: NDArray[np.integer], modulation: str) -> NDArray[np.complex128]:
    """Generate modulated symbols."""
    int_modtype = modulation.lower()

    assert int_modtype in ["pi/2-bpsk", "bpsk", "qpsk", "16qam", "64qam", "256qam"], "modulation type is incorrect"
    assert len(databits) > 0, "length of databits must be greater 0"

    if int_modtype == "bpsk":
        res_arr = np.zeros(len(databits), dtype=(complex))
        for idx, sample in enumerate(databits):
            res_arr[idx] = (1 - 2 * sample) + 1j * (1 - 2 * sample)
        res_arr = [x / np.sqrt(2) for x in res_arr]

    elif int_modtype == "pi/2-bpsk":
        res_arr = np.zeros(len(databits), dtype=(complex))
        for idx, sample in enumerate(databits):
            if idx % 2:
                res_arr[idx] = (2 * sample - 1) + 1j * (1 - 2 * sample)
            else:
                res_arr[idx] = (1 - 2 * sample) + 1j * (1 - 2 * sample)
        res_arr = [x / np.sqrt(2) for x in res_arr]

    elif int_modtype == "qpsk":
        assert not (len(databits) % 2), "length of databits must be multiple of 2"
        res_arr = np.zeros((len(databits) // 2), dtype=(complex))
        chunks = np.array_split(databits, len(databits) // 2)
        for idx, sample in enumerate(chunks):
            res_arr[idx] = (1 - 2 * sample[0]) + 1j * (1 - 2 * sample[1])
        res_arr = [x / np.sqrt(2) for x in res_arr]

    elif int_modtype == "16qam":
        assert not (len(databits) % 4), "length of databits must be multiple of 4"
        res_arr = np.zeros((len(databits) // 4), dtype=(complex))
        chunks = np.array_split(databits, len(databits) // 4)
        for idx, sample in enumerate(chunks):
            res_arr[idx] = ((1 - 2 * sample[0]) * (2 - (1 - 2 * sample[2]))) + 1j * (
                (1 - 2 * sample[1]) * (2 - (1 - 2 * sample[3]))
            )
        res_arr = [x / np.sqrt(10) for x in res_arr]

    elif int_modtype == "64qam":
        assert not (len(databits) % 6), "length of databits must be multiple of 6"
        res_arr = np.zeros((len(databits) // 6), dtype=(complex))
        chunks = np.array_split(databits, len(databits) // 6)
        for idx, sample in enumerate(chunks):
            res_arr[idx] = ((1 - 2 * sample[0]) * (4 - (1 - 2 * sample[2]) * (2 - (1 - 2 * sample[4])))) + 1j * (
                (1 - 2 * sample[1]) * (4 - (1 - 2 * sample[3]) * (2 - (1 - 2 * sample[5])))
            )
        res_arr = [x / np.sqrt(42) for x in res_arr]

    elif int_modtype == "256qam":
        assert not (len(databits) % 8), "length of databits must be multiple of 8"
        res_arr = np.zeros((len(databits) // 8), dtype=(complex))
        chunks = np.array_split(databits, len(databits) // 8)
        for idx, sample in enumerate(chunks):
            res_arr[idx] = (
                (1 - 2 * sample[0]) * (8 - (1 - 2 * sample[2]) * (4 - (1 - 2 * sample[4]) * (2 - (1 - 2 * sample[6]))))
            ) + 1j * (
                (1 - 2 * sample[1]) * (8 - (1 - 2 * sample[3]) * (4 - (1 - 2 * sample[5]) * (2 - (1 - 2 * sample[7]))))
            )
        res_arr = [x / np.sqrt(170) for x in res_arr]
    else:
        raise AssertionError(f"unreachable: unsupported modulation type {int_modtype}")

    return np.array(res_arr)


# 16QAM constellation:
#                Q
#  1011    1001  |   0001  0011
#  1010    1000  |   0000  0010
# ---------------------------------> I
#  1110    1100  |   0100  0110
#  1111    1101  |   0101  0111
def _16QAM_table() -> NDArray[np.complex128]:
    table = np.empty(16, "complex")
    QAM16_LEVEL_1 = 1 / np.sqrt(10)
    QAM16_LEVEL_2 = 3 / np.sqrt(10)
    table[0] = QAM16_LEVEL_1 + 1j * QAM16_LEVEL_1
    table[1] = QAM16_LEVEL_1 + 1j * QAM16_LEVEL_2
    table[2] = QAM16_LEVEL_2 + 1j * QAM16_LEVEL_1
    table[3] = QAM16_LEVEL_2 + 1j * QAM16_LEVEL_2
    table[4] = QAM16_LEVEL_1 - 1j * QAM16_LEVEL_1
    table[5] = QAM16_LEVEL_1 - 1j * QAM16_LEVEL_2
    table[6] = QAM16_LEVEL_2 - 1j * QAM16_LEVEL_1
    table[7] = QAM16_LEVEL_2 - 1j * QAM16_LEVEL_2
    table[8] = -QAM16_LEVEL_1 + 1j * QAM16_LEVEL_1
    table[9] = -QAM16_LEVEL_1 + 1j * QAM16_LEVEL_2
    table[10] = -QAM16_LEVEL_2 + 1j * QAM16_LEVEL_1
    table[11] = -QAM16_LEVEL_2 + 1j * QAM16_LEVEL_2
    table[12] = -QAM16_LEVEL_1 - 1j * QAM16_LEVEL_1
    table[13] = -QAM16_LEVEL_1 - 1j * QAM16_LEVEL_2
    table[14] = -QAM16_LEVEL_2 - 1j * QAM16_LEVEL_1
    table[15] = -QAM16_LEVEL_2 - 1j * QAM16_LEVEL_2
    return table


def nrSymbolDemodulate(
    input: NDArray[np.complex128],
    mod: Literal["BPSK", "QPSK", "16QAM", "64QAM", "256QAM"],
    nVar: float = 1e-10,
    DecisionType: Literal["soft", "hard"] = "soft",
) -> NDArray[np.floating] | NDArray[np.integer]:
    """Demodulate and convert symbols to bits."""
    r_i = np.real(input)
    r_q = np.imag(input)
    if mod == "BPSK":
        output = r_i + r_q
        K = 1
    elif mod == "QPSK":
        output = np.zeros(len(input) * 2, dtype="float")
        output[0::2] = r_i
        output[1::2] = r_q
        K = 1
    elif mod == "16QAM":
        d = 1 / np.sqrt(10)
        output = np.zeros(len(input) * 4, dtype="float")
        output[0::4] = r_i
        output[1::4] = r_q
        output[2::4] = 2 * d - np.abs(r_i)
        output[3::4] = 2 * d - np.abs(r_q)
        K = 4 * d
    elif mod == "64QAM":
        d = 1 / np.sqrt(42)
        output = np.zeros(len(input) * 6, dtype="float")
        output[0::6] = r_i
        output[1::6] = r_q
        output[2::6] = 4 * d - np.abs(r_i)
        output[3::6] = 4 * d - np.abs(r_q)
        output[4::6] = 2 * d - np.abs(4 * d - np.abs(r_i))
        output[5::6] = 2 * d - np.abs(4 * d - np.abs(r_q))
        K = 4 * d
    elif mod == "256QAM":
        d = 1 / np.sqrt(170)
        output = np.zeros(len(input) * 8, dtype="float")
        output[0::8] = r_i
        output[1::8] = r_q
        output[2::8] = 8 * d - np.abs(r_i)
        output[3::8] = 8 * d - np.abs(r_q)
        output[4::8] = 4 * d - np.abs(8 * d - np.abs(r_i))
        output[5::8] = 4 * d - np.abs(8 * d - np.abs(r_q))
        output[6::8] = 2 * d - np.abs(4 * d - np.abs(8 * d - np.abs(r_i)))
        output[7::8] = 2 * d - np.abs(4 * d - np.abs(8 * d - np.abs(r_q)))
        K = 4 * d
    else:
        raise NotImplementedError(mod)

    if DecisionType == "soft":
        output *= K / nVar
    else:
        output = (output < 0).astype(int)
    return output


def nrLayerMap(
    in_symbols: NDArray[np.complexfloating] | list[NDArray[np.complexfloating]], nLayers: int
) -> NDArray[np.float64]:
    """Layer mapping of modulated and scrambled codewords."""

    # Check number of modulation symbols from either one or two codewords
    if isinstance(in_symbols, np.ndarray):
        if in_symbols.ndim == 2 and in_symbols.shape[1] == 1:
            in_symbols = [in_symbols]
            codewords = 1
        else:
            raise ValueError("Input array should have a single column (shape Mx1).")
    elif isinstance(in_symbols, list):
        if len(in_symbols) == 1:
            if isinstance(in_symbols[0], np.ndarray) and in_symbols[0].ndim == 2 and in_symbols[0].shape[1] == 1:
                in_symbols = [in_symbols[0]]
                codewords = 1
            else:
                raise ValueError("Each array in the list should have a single column (shape Mx1).")
        elif len(in_symbols) == 2:
            if all(isinstance(arr, np.ndarray) and arr.ndim == 2 and arr.shape[1] == 1 for arr in in_symbols):
                codewords = 2
            else:
                raise ValueError("Each array in the list should have a single column (shape Mx1).")
        else:
            raise ValueError("Input list should contain either 1 or 2 arrays.")
    else:
        raise TypeError("Input must be a numpy array or a list of numpy arrays.")

    # Check number of number of transmission layers
    if not isinstance(nLayers, int):
        raise TypeError("nLayers must be an integer.")
    if nLayers < 1 or nLayers > 8:
        raise ValueError("nLayers must be an integer between 1 and 8.")

    # Codeword to layer mapping (1 codewords)
    if codewords == 1:
        if nLayers == 1 or nLayers == 2 or nLayers == 3 or nLayers == 4:
            m = in_symbols[0].shape[0] / nLayers
            n = nLayers
            out = np.array([[m, n]])
        else:
            raise ValueError("nLayers must be an integer between 1 to 4 for 1 codewords.")

    # Codeword to layer mapping (2 codewords)
    elif codewords == 2:
        if nLayers == 6 or nLayers == 8:
            m_one = in_symbols[0].shape[0] / (nLayers / 2)
            m_two = in_symbols[1].shape[0] / (nLayers / 2)
            n = nLayers
            if m_one == m_two:
                out = np.array([[m_one, n]])
            else:
                raise ValueError("in_symbols value does not match between codewords 1 and 2")
        elif nLayers == 5:
            m_one = in_symbols[0].shape[0] / 2
            m_two = in_symbols[1].shape[0] / 3
            n = nLayers
            if m_one == m_two:
                out = np.array([[m_one, n]])
            else:
                raise ValueError("in_symbols value does not match between codewords 1 and 2")
        elif nLayers == 7:
            m_one = in_symbols[0].shape[0] / 3
            m_two = in_symbols[1].shape[0] / 4
            n = nLayers
            if m_one == m_two:
                out = np.array([[m_one, n]])
            else:
                raise ValueError("in_symbols value does not match between codewords 1 and 2")
        else:
            raise ValueError("nLayers must be an integer between 5 to 8 for 2 codewords.")
    else:
        raise AssertionError(f"unreachable: unsupported number of codewords {codewords}")
    return out


# # Example usage for one codeword (Array)
# out = nrLayerMap(np.ones((40, 1)), 4)
# print(out)

# # Example usage for one codeword (Array in List)
# out = nrLayerMap([np.ones((40, 1))], 4)
# print(out)

# # Example usage for two codeword (Array in List)
# out = nrLayerMap([np.ones((20, 1)), np.ones((30, 1))], 5)
# print(out)


def nrTransformPrecode(modSym: NDArray[np.complex128], mrb: int) -> NDArray[np.complex128]:
    """Generate transform precoded symbols."""
    mrb = int(mrb)
    assert modSym.shape[0] % (mrb * 12) == 0, "input number of rows must be an integer multiple of mrb * 12"
    return (np.fft.fft(modSym.reshape(int(modSym.shape[0] / (mrb * 12)), mrb * 12)) * 1 / np.sqrt(mrb * 12)).ravel()


def nrTransformDeprecode(modSym: NDArray[np.complex128], mrb: int) -> NDArray[np.complex128]:
    """Recover transform deprecoded symbols."""
    mrb = int(mrb)
    assert modSym.shape[0] % (mrb * 12) == 0, "input number of rows must be an integer multiple of mrb * 12"
    return (np.fft.ifft(modSym.reshape(int(modSym.shape[0] / (mrb * 12)), mrb * 12)) * np.sqrt(mrb * 12)).ravel()
