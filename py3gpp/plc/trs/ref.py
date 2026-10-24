# Ref: https://ch.mathworks.com/help/5g/ref/nrtbs.html#d124e53763
# Ref: TS 38.214 Sections 5.1.3.2
from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray


def nrTBS(
    mod: str | list[str] | tuple[str, ...],
    nlayers: int,
    nPRB: int,
    NREPerPRB: int,
    tcr: float | list[float] | tuple[float, ...],
    xOh: int = 0,
    tbScaling: float | list[float] | tuple[float, float] = 1,
) -> int | NDArray[np.int_]:

    ### Pre-defined table ###

    modulation_schemes = {"pi/2-BPSK": 1, "QPSK": 2, "16QAM": 4, "64QAM": 6, "256QAM": 8, "1024QAM": 10}

    tbs_values = [
        24,
        32,
        40,
        48,
        56,
        64,
        72,
        80,
        88,
        96,
        104,
        112,
        120,
        128,
        136,
        144,
        152,
        160,
        168,
        176,
        184,
        192,
        208,
        224,
        240,
        256,
        272,
        288,
        304,
        320,
        336,
        352,
        368,
        384,
        408,
        432,
        456,
        480,
        504,
        528,
        552,
        576,
        608,
        640,
        672,
        704,
        736,
        768,
        808,
        848,
        888,
        928,
        984,
        1032,
        1064,
        1128,
        1160,
        1192,
        1224,
        1256,
        1288,
        1320,
        1352,
        1416,
        1480,
        1544,
        1608,
        1672,
        1736,
        1800,
        1864,
        1928,
        2024,
        2088,
        2152,
        2216,
        2280,
        2408,
        2472,
        2536,
        2600,
        2664,
        2728,
        2792,
        2856,
        2976,
        3104,
        3240,
        3368,
        3496,
        3624,
        3752,
        3824,
    ]

    ### Input check ###

    # nlayers
    if not (1 <= nlayers <= 8):
        raise ValueError("nlayers must be an integer between 1 and 8")

    # nPRB
    if nPRB < 0:
        raise ValueError("nPRB must be a nonnegative integer")

    # NREPerPRB
    if NREPerPRB < 0:
        raise ValueError("NREPerPRB must be a nonnegative integer")

    # xOh
    if not isinstance(xOh, int) or xOh < 0:
        raise ValueError("xOh must be a nonnegative integer")

    # tbScaling
    if isinstance(tbScaling, (int, float)):
        if not (0 < tbScaling <= 1):
            raise ValueError("tbScaling must be a scalar in the range (0, 1]")
    elif isinstance(tbScaling, (list, tuple)) and len(tbScaling) == 2:
        if not (0 < tbScaling[0] <= 1) or not (0 < tbScaling[1] <= 1):
            raise ValueError("Each element in tbScaling must be in the range (0, 1]")
    else:
        raise ValueError("Invalid type or format for tbScaling")

    # tcr
    if isinstance(tcr, (float, int)):
        tcr = [tcr]
        if not (0 <= tcr[0] <= 1):
            raise ValueError("tcr must be a scalar between 0 and 1")
    elif isinstance(tcr, (list, tuple)):
        if len(tcr) != len(mod):
            raise ValueError("The number of elements in 'tcr' must match the number of codewords")
        for t in tcr:
            if not (0 <= t <= 1):
                raise ValueError("Each element in 'tcr' must be between 0 and 1")
    else:
        raise ValueError("Invalid type for 'tcr'. It must be a scalar, list, or tuple")

    # mod
    if isinstance(mod, (str, list, tuple)):
        if isinstance(mod, str):
            mod = [mod]
        if len(mod) <= 2:
            if all(m in modulation_schemes for m in mod):
                bits_per_symbol = [modulation_schemes[m] for m in mod]
            else:
                raise ValueError("Invalid modulation scheme(s) in the input")
        else:
            raise ValueError("Input 'mod' must be a single valid modulation or a list/tuple of 2 valid modulations")
    else:
        raise ValueError(
            "Invalid type for 'mod'. It must be a single valid modulation or a list/tuple of 2 valid modulations"
        )

    ### Calculate N Info for each codeword ###

    n_info = []
    for i in range(len(mod)):
        n_re = min(156, (NREPerPRB - xOh)) * (nPRB // len(mod))  # Divide nPRB into equal parts
        n_info.append(tbScaling * n_re * tcr[i] * bits_per_symbol[i] * nlayers)

    tbs = []
    for i in range(len(n_info)):
        # Check conditions to set tbs to 0
        if NREPerPRB == 0 or nPRB == 0 or NREPerPRB < xOh:
            tbs.append(0)
        else:
            # Calculate DL TBS for each codeword
            if n_info[i] <= 3824:
                n = max(3, np.floor(abs(np.log2(n_info[i]) - 6)))
                n_info_ = max(24, (2**n) * np.floor(abs(n_info[i] / (2**n))))
                closest_tbs = min(filter(lambda tbs: tbs >= n_info_, tbs_values), key=lambda tbs: abs(tbs - n_info_))
                n_info[i] = max(n_info_, closest_tbs)
            else:
                n = np.floor(abs(np.log2(n_info[i] - 24) - 5))
                n_info_ = max(3840, (2**n) * round((n_info[i] - 24) / (2**n)))
                if tcr[i] <= 0.25:
                    c = np.ceil(abs((n_info_ + 24) / (3816)))
                    n_info[i] = (8 * c * np.ceil(abs((n_info_ + 24) / (8 * c)))) - 24
                else:
                    if n_info_ > 8424:
                        c = np.ceil(abs((n_info_ + 24) / (8424)))
                        n_info[i] = (8 * c * np.ceil(abs((n_info_ + 24) / (8 * c)))) - 24
                    else:
                        n_info[i] = (8 * np.ceil(abs((n_info_ + 24) / 8))) - 24

            tbs.append(int(n_info[i]))

    ### Input check ###
    if len(tbs) == 1:
        tbs = int(tbs[0])  # Convert to integer
    else:
        tbs = np.array(tbs)  # Convert to NumPy array

    return tbs


# # Example usage for one codeword
# modulation = '16QAM'
# nlayers = 4
# nPRB = 52
# NREPerPRB = 120
# tcr = 0.48
# xOh = 6
# tbScaling = 0.25
# tbs = nrTBS(modulation, nlayers, nPRB, NREPerPRB, tcr, xOh, tbScaling)
# print(f'TBS for One Codeword: {tbs}')

# # Example usage for two codewords
# modulation = ['QPSK', '64QAM']
# nlayers = 8
# nPRB = 106
# NREPerPRB = 100
# tcr = [0.3701, 0.4277]
# xOh = 0
# tbScaling = 1
# tbs = nrTBS(modulation, nlayers, nPRB, NREPerPRB, tcr, xOh, tbScaling)
# print(f'TBS for Two Codewords: {tbs}')


def qm_to_mod(qm: int) -> Literal["BPSK", "QPSK", "16QAM", "64QAM", "256QAM"]:
    if qm == 1:
        return "BPSK"
    if qm == 2:
        return "QPSK"
    if qm == 4:
        return "16QAM"
    if qm == 6:
        return "64QAM"
    if qm == 8:
        return "256QAM"
    assert False, f"modulation order = {qm} is not supported"
    return 0


class qam64_table:
    def __init__(self) -> None:
        self._table: NDArray[np.int_] = np.zeros((4, 29), int)
        self._table[0, :] = np.arange(self._table.shape[1])
        self._table[1, :] = np.array(
            [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]
        )
        self._table[2, :] = np.array(
            [
                120,
                157,
                193,
                251,
                308,
                379,
                449,
                526,
                602,
                679,
                340,
                378,
                434,
                490,
                553,
                616,
                658,
                438,
                466,
                517,
                567,
                616,
                666,
                719,
                772,
                822,
                873,
                910,
                948,
            ]
        )
        self._table[3, :] = np.array(
            [
                0.2344,
                0.3066,
                0.377,
                0.4902,
                0.6016,
                0.7402,
                0.877,
                1.0273,
                1.1758,
                1.3262,
                1.3281,
                1.4766,
                1.6953,
                1.9141,
                2.1602,
                2.4063,
                2.5703,
                2.5664,
                2.7305,
                3.0293,
                3.3223,
                3.6094,
                3.9023,
                4.2129,
                4.5234,
                4.8164,
                5.1152,
                5.332,
                5.5547,
            ]
        )

    def Qm(self, mcs: int) -> int:
        return self._table[1, mcs]

    def Modulation(self, mcs: int) -> Literal["BPSK", "QPSK", "16QAM", "64QAM", "256QAM"]:
        return qm_to_mod(self._table[1, mcs])

    def Rate(self, mcs: int) -> float:
        return self._table[2, mcs] / 1024

    def SpectralEfficiency(self, mcs: int) -> float:
        return self._table[3, mcs]


class qam64lowse_table:
    def __init__(self) -> None:
        self._table: NDArray[np.int_] = np.zeros((4, 29), int)
        self._table[0, :] = np.arange(self._table.shape[1])
        self._table[1, :] = np.array(
            [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6]
        )
        self._table[2, :] = np.array(
            [
                30,
                40,
                50,
                64,
                78,
                99,
                120,
                157,
                193,
                251,
                308,
                379,
                449,
                526,
                602,
                340,
                378,
                434,
                490,
                553,
                616,
                438,
                466,
                517,
                567,
                616,
                666,
                719,
                772,
            ]
        )
        self._table[3, :] = np.array(
            [
                0.0586,
                0.0781,
                0.0977,
                0.125,
                0.1523,
                0.1934,
                0.2344,
                0.3066,
                0.377,
                0.4902,
                0.6016,
                0.7402,
                0.877,
                1.0273,
                1.1758,
                1.3281,
                1.4766,
                1.6953,
                1.9141,
                2.1602,
                2.4063,
                2.5664,
                2.7305,
                3.0293,
                3.3223,
                3.6094,
                3.9023,
                4.2129,
                4.5234,
            ]
        )

    def Qm(self, mcs: int) -> int:
        return self._table[1, mcs]

    def Modulation(self, mcs: int) -> Literal["BPSK", "QPSK", "16QAM", "64QAM", "256QAM"]:
        return qm_to_mod(self._table[1, mcs])

    def Rate(self, mcs: int) -> float:
        return self._table[2, mcs] / 1024

    def SpectralEfficiency(self, mcs: int) -> float:
        return self._table[3, mcs]


class qam256_table:
    def __init__(self) -> None:
        self._table: NDArray[np.int_] = np.zeros((4, 28), int)
        self._table[0, :] = np.arange(self._table.shape[1])
        self._table[1, :] = np.array(
            [2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 8, 8, 8, 8, 8, 8, 8, 8]
        )
        self._table[2, :] = np.array(
            [
                120,
                193,
                308,
                449,
                602,
                378,
                434,
                490,
                553,
                616,
                658,
                466,
                517,
                567,
                616,
                666,
                719,
                772,
                822,
                873,
                682.5,
                711,
                754,
                797,
                841,
                885,
                916.5,
                948,
            ]
        )
        self._table[3, :] = np.array(
            [
                0.2344,
                0.377,
                0.6016,
                0.877,
                1.1758,
                1.4766,
                1.6953,
                1.9141,
                2.1602,
                2.4063,
                2.5703,
                2.7305,
                3.0293,
                3.3223,
                3.6094,
                3.9023,
                4.2129,
                4.5234,
                4.8164,
                5.1152,
                5.332,
                5.5547,
                5.8906,
                6.2266,
                6.5703,
                6.9141,
                7.1602,
                7.4063,
            ]
        )

    def Qm(self, mcs: int) -> int:
        return self._table[1, mcs]

    def Modulation(self, mcs: int) -> Literal["BPSK", "QPSK", "16QAM", "64QAM", "256QAM"]:
        return qm_to_mod(self._table[1, mcs])

    def Rate(self, mcs: int) -> float:
        return self._table[2, mcs] / 1024

    def SpectralEfficiency(self, mcs: int) -> float:
        return self._table[3, mcs]


class pdsch_mcs_table_class:
    def __init__(self) -> None:
        self.QAM64Table: qam64_table = qam64_table()
        self.QAM64LowSETable: qam64lowse_table = qam64lowse_table()
        self.QAM256Table: qam256_table = qam256_table()


def nrPDSCHMCSTables() -> pdsch_mcs_table_class:
    return pdsch_mcs_table_class()


if __name__ == "__main__":
    table = nrPDSCHMCSTables().QAM64Table
    mcs = 0
    print(f"mcs = {mcs}, modulation = {table.Modulation(mcs)}, rate = {table.Rate(mcs)}")
    mcs = 16
    print(f"mcs = {mcs}, modulation = {table.Modulation(mcs)}, rate = {table.Rate(mcs)}")
