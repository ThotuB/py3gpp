from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from py3gpp.helper import generate_5g_ranking, polar_precode_interleave


def nrPolarEncode(payload: NDArray[np.int_], E: int, nmax: int = 9, iil: bool = False) -> NDArray[np.int_]:
    """Polar encoding."""
    K = payload.shape[0]
    assert not (iil and K > 164), "iil is not supported for K > 164"
    _, info_pos = generate_5g_ranking(k=K, n=2**nmax)
    N = 2**nmax
    u = np.zeros(N).astype(int)
    if iil:
        u[info_pos] = payload.astype(int)[polar_precode_interleave(K)]
    else:
        u[info_pos] = payload.astype(int)
    G_N = int(1)
    for _ in range(nmax):
        G_N = np.kron(G_N, np.array([[1, 0], [1, 1]]).astype(int))
    cw = np.mod(np.matmul(u, G_N), 2)
    return cw


def Polar_SC_decoder(N: int, frozen_pos: NDArray[np.int_], r: NDArray[np.floating]) -> NDArray[np.int_]:
    n = np.log2(N).astype(int)
    L = np.zeros((n + 1, N))
    ucap = np.zeros((n + 1, N))
    ns = np.zeros(2 * N - 1, int)  # node state vector
    L[0, :] = r
    node = depth = done = 0
    while done == 0:
        # print(f'd = {depth}, node = {node}')
        if depth == n:
            ucap[n, node] = 0 if ((L[n, node] >= 0) or (node in frozen_pos)) else 1
            if node == N - 1:
                done = 1
            else:
                node = node // 2  # go to parent
                depth -= 1
        else:
            npos = int(2**depth - 1 + node)
            temp = 2 ** (n - depth)
            ctemp = temp // 2
            Ln = L[depth, temp * node : temp * (node + 1)]  # incoming beliefs
            a = Ln[: temp // 2]
            b = Ln[temp // 2 :]
            lnode = 2 * node  # left node
            rnode = 2 * node + 1  # right node
            if ns[npos] == 0:
                node = lnode  # go to left node
                depth += 1
                L[depth, ctemp * node : ctemp * (node + 1)] = (
                    # cannot use np.sign() because np.sign(0) = 0 !!
                    (1 - 2 * (a < 0))
                    * (1 - 2 * (b < 0))
                    * np.minimum(np.abs(a), np.abs(b))  # minsum-function
                )
            elif ns[npos] == 1:
                ucapn = ucap[depth + 1, ctemp * lnode : ctemp * (lnode + 1)]  # incoming decisions from left child
                node = rnode  # go to right node
                depth += 1
                L[depth, ctemp * node : ctemp * (node + 1)] = b + (1 - 2 * ucapn) * a  # g-function
            elif ns[npos] == 2:
                ucapl = ucap[depth + 1, ctemp * lnode : ctemp * (lnode + 1)]
                ucapr = ucap[depth + 1, ctemp * rnode : ctemp * (rnode + 1)]
                ucap[depth, temp * node : temp * (node + 1)] = np.append(np.mod(ucapl + ucapr, 2), ucapr)  # combine
                node = node // 2  # go to parent node
                depth -= 1
            else:
                assert False
            ns[npos] += 1
    return ucap.astype(int)[n, :]


# rec: Rate-recovered input, LLRs, length must be power of two
# K: length of information block in bits, includes CRC
# E: rate-matched output length in bits
# L: length of decoding list
# CRClen: number of appended CRC bits
def nrPolarDecode(
    rec: NDArray[np.floating],
    K: int,
    E: int,
    L: int,
    padCRC: bool = False,
    nmax: Literal[9, 10] = 9,
    iil: bool = True,
    CRClen: Literal[6, 11, 24] = 24,
) -> NDArray[np.int_]:
    """Polar decoding."""
    if CRClen not in (6, 11, 24):
        print("Error: invalid CRClen value!")
        exit()
    if nmax not in (9, 10):
        print("Error: invalid nmax value!")
        exit()
    # TODO: what to do with E argument, it is currently deducted from rec shape
    N = 2**nmax
    frozen_pos, info_pos = generate_5g_ranking(K, N)

    decoded = Polar_SC_decoder(N, frozen_pos, rec)[info_pos]

    if iil:
        # deinterleave
        p_IL = polar_precode_interleave(K)
        decoded2 = np.empty(decoded.shape, int)
        np.put(decoded2, p_IL, decoded)
    else:
        decoded2 = decoded

    return decoded2


def subblock_interleaving(u: NDArray[np.int_]) -> NDArray[np.int_]:
    N = u.shape[-1]
    assert np.mod(N, 32) == 0, "length for sub-block interleaving must be a multiple of 32."
    y = np.zeros_like(u)
    # Permutation according to Tab 5.4.1.1-1 in 38.212
    perm = np.array(
        [
            0,
            1,
            2,
            4,
            3,
            5,
            6,
            7,
            8,
            16,
            9,
            17,
            10,
            18,
            11,
            19,
            12,
            20,
            13,
            21,
            14,
            22,
            15,
            23,
            24,
            25,
            26,
            28,
            27,
            29,
            30,
            31,
        ]
    )

    for n in range(N):
        i = int(32 * n / N)
        j = int(perm[i] * N / 32 + np.mod(n, N / 32))
        y[n] = u[j]

    return y


def nrRateMatchPolar(enc: NDArray[np.int_], K: int, E: int, ibil: bool = False) -> NDArray[np.int_]:
    """Rate matching for Polar encoded data."""
    # TODO: for what is the parameter K??
    N = enc.shape[0]
    d = np.zeros(N, int)
    d = enc[subblock_interleaving(np.arange(N))]
    y = np.zeros(E, int)
    if N <= E:
        # repetition
        y[:N] = d[:N]
        for k in range(N, E):
            y[k] += d[k % N]
    else:
        # TODO: implement shortening und puncturing
        print("Error!")
        exit()
    if ibil == True:
        print("Error: interleaving of coded bits is not implemented!")
        exit()
    return y


def nrRateRecoverPolar(
    llr: NDArray[np.floating], K: int, N: int, ibil: bool = False, discardRepetition: bool = True
) -> NDArray[np.floating]:
    """Recover rate matched Polar data."""
    E = llr.shape[0]
    if N <= E:
        # undo repetition
        y = np.copy(llr[:N])
        if discardRepetition == False:
            for k in range(N, E):
                y[k % N] += llr[k]
    else:
        # TODO: implement shortening und puncturing
        print("Error!")
        exit()
    if ibil == True:
        print("Error: interleaving of coded bits is not implemented!")
        exit()
    d = np.zeros(N)
    np.put(d, subblock_interleaving(np.arange(N)), y)
    return d
