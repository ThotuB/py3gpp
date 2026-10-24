from __future__ import annotations

from typing import Literal

import numpy as np
import scipy as sp
from importlib_resources import as_file, files  # importlib.resources only works for Python >= 3.9
from numpy.typing import NDArray

from py3gpp import codes
from py3gpp.dl.ch.trs.dlsch import getCBSInfo, getZarray, getZlist, nrDLSCHInfo
from py3gpp.plc.trs.crc import nrCRCDecode, nrCRCEncode

Modulation = Literal["pi/2-BPSK", "BPSK", "QPSK", "16QAM", "64QAM", "256QAM"]


def nrCodeBlockSegmentLDPC(blk: NDArray[np.int_], bgn: Literal[1, 2]) -> NDArray[np.int_]:
    assert bgn in [1, 2], "bgn must be in [1, 2]"
    cbsInfo = getCBSInfo(len(blk), bgn)
    assert cbsInfo["Lcb"] in [0, 24], f'Error: Lcb = {cbsInfo["Lcb"]} is not supported!'
    if len(blk.shape) == 1:
        blk = np.expand_dims(blk, axis=1)
    cbs = np.ones((cbsInfo["K"], cbsInfo["C"]), dtype=int) * (-1)  # fill bits are -1
    idx = 0
    for i in np.arange(cbsInfo["C"]):
        if i < cbsInfo["C"] - 1:
            if cbsInfo["Lcb"] == 0:
                cbs[0 : cbsInfo["CBZ"], i] = blk[idx:][: cbsInfo["CBZ"]]
            elif cbsInfo["Lcb"] == 24:
                cbs[0 : cbsInfo["CBZ"] + cbsInfo["Lcb"], i] = nrCRCEncode(blk[idx:, 0][: cbsInfo["CBZ"]], "24B", 0)[
                    :, 0
                ]
            idx += cbsInfo["CBZ"]
        else:
            cbs[0 : cbsInfo["CBZ"], i] = 0
            if cbsInfo["Lcb"] == 0:
                cbs[0 : len(blk) - idx, i] = blk[idx:, 0]
            elif cbsInfo["Lcb"] == 24:
                blk_padded = np.zeros(cbsInfo["CBZ"])
                blk_padded[: len(blk) - idx] = blk[idx:, 0]
                cbs[0 : cbsInfo["CBZ"] + cbsInfo["Lcb"], i] = nrCRCEncode(blk_padded, "24B", 0)[:, 0]

    return cbs


def nrCodeBlockDesegmentLDPC(
    cbs: NDArray[np.int_], bgn: Literal[1, 2], blklen: int
) -> tuple[NDArray[np.floating], bool]:
    assert len(cbs.shape) == 2
    blk = None
    err = False
    blk = np.zeros(blklen)
    if cbs.shape[1] == 1:
        blk = cbs[:blklen, 0]
        # there is no appended CRC when there is only one segment
    else:
        cbsInfo = getCBSInfo(blklen, bgn)
        idx = 0
        for i in np.arange(cbsInfo["C"]):
            if i < cbsInfo["C"] - 1:
                blk[idx:][: cbsInfo["CBZ"]] = cbs[0 : cbsInfo["CBZ"], i]
                _, crc = nrCRCDecode(cbs[0 : cbsInfo["CBZ"] + cbsInfo["Lcb"], i], "24B")
                idx += cbsInfo["CBZ"]
            else:
                blk[idx:][: blklen - idx] = cbs[0 : blklen - idx, i]
                _, crc = nrCRCDecode(cbs[0 : cbsInfo["CBZ"] + cbsInfo["Lcb"], i], "24B")

            if crc != 0:
                err = True
                print(f"nrCodeBlockDesegmentLDPC: crc error in segment {i}")

    return blk, err


def _load_basegraph(i_ls: int, bgn: int) -> NDArray[np.float64]:
    if i_ls > 7:
        raise ValueError("i_ls too large.")

    if i_ls < 0:
        raise ValueError("i_ls cannot be negative.")

    # csv files are taken from 38.212 and dimension is explicitly given
    if bgn == 1:
        bm = np.zeros([46, 68]) - 1  # init matrix with -1 (None positions)
    elif bgn == 2:
        bm = np.zeros([42, 52]) - 1  # init matrix with -1 (None positions)
    else:
        raise ValueError("Basegraph not supported.")

    # and load the basegraph from csv format in folder "codes"
    source = source = files(codes).joinpath(f"bg{bgn}.csv")
    with as_file(source) as code:
        bg_csv = np.genfromtxt(code, delimiter=";")

    # reconstruct BG for given i_ls
    r_ind = 0
    for r in np.arange(2, bg_csv.shape[0]):
        # check for next row index
        if not np.isnan(bg_csv[r, 0]):
            r_ind = int(bg_csv[r, 0])
        c_ind = int(bg_csv[r, 1])  # second column in csv is column index
        value = bg_csv[r, i_ls + 2]  # i_ls entries start at offset 2
        bm[r_ind, c_ind] = value

    return bm


# This function is from Sionna
def _lift_basegraph(bm: NDArray[np.float64], z: int) -> sp.sparse.csr_matrix:
    """Lift basegraph with lifting factor ``z`` and shifted identities as
    defined by the entries of ``bm``."""

    num_nonzero = np.sum(bm >= 0)  # num of non-neg elements in bm

    # init all non-zero row/column indices
    r_idx = np.zeros(z * num_nonzero)
    c_idx = np.zeros(z * num_nonzero)
    data = np.ones(z * num_nonzero)

    # row/column indices of identity matrix for lifting
    im = np.arange(z)

    idx = 0
    for r in range(bm.shape[0]):
        for c in range(bm.shape[1]):
            if bm[r, c] == -1:  # -1 is used as all-zero matrix placeholder
                pass  # do nothing (sparse)
            else:
                # roll matrix by bm[r,c]
                c_roll = np.mod(im + bm[r, c], z)
                # append rolled identity matrix to pcm
                r_idx[idx * z : (idx + 1) * z] = r * z + im
                c_idx[idx * z : (idx + 1) * z] = c * z + c_roll
                idx += 1

    # generate lifted sparse matrix from indices
    pcm = sp.sparse.csr_matrix((data, (r_idx, c_idx)), shape=(z * bm.shape[0], z * bm.shape[1]))
    return pcm


# This function is from Sionna
def _gen_submat(
    bm: NDArray[np.float64], k_b: int, z: int, bgn: int
) -> tuple[sp.sparse.csr_matrix, sp.sparse.csr_matrix, sp.sparse.csr_matrix, sp.sparse.csr_matrix]:
    """Split the basegraph into multiple sub-matrices such that efficient
    encoding is possible.
    """
    g = 4  # code property (always fixed for 5G)
    mb = bm.shape[0]  # number of CN rows in basegraph (BG property)

    bm_a = bm[0:g, 0:k_b]
    bm_b = bm[0:g, k_b : (k_b + g)]
    bm_c1 = bm[g:mb, 0:k_b]
    bm_c2 = bm[g:mb, k_b : (k_b + g)]

    # H could be sliced immediately (but easier to implement if based on B)
    hm_a = _lift_basegraph(bm_a, z)

    # not required for encoding, but helpful for debugging
    # hm_b = self._lift_basegraph(bm_b, z)

    hm_c1 = _lift_basegraph(bm_c1, z)
    hm_c2 = _lift_basegraph(bm_c2, z)

    hm_b_inv = _find_hm_b_inv(bm_b, z, bgn)

    return hm_a, hm_b_inv, hm_c1, hm_c2


# This function is from Sionna
def _find_hm_b_inv(bm_b: NDArray[np.float64], z: int, bgn: int) -> sp.sparse.csr_matrix:
    """For encoding we need to find the inverse of `hm_b` such that
    `hm_b^-1 * hm_b = I`.

    Could be done sparse
    For BG1 the structure of hm_b is given as (for all values of i_ls)
    hm_b =
    [P_A I 0 0
        P_B I I 0
        0 0 I I
        P_A 0 0 I]
    where P_B and P_A are Shifted identities.

    The inverse can be found by solving a linear system of equations
    hm_b_inv =
    [P_B^-1, P_B^-1, P_B^-1, P_B^-1,
        I + P_A*P_B^-1, P_A*P_B^-1, P_A*P_B^-1, P_A*P_B^-1,
        P_A*P_B^-1, P_A*P_B^-1, I+P_A*P_B^-1, I+P_A*P_B^-1,
        P_A*P_B^-1, P_A*P_B^-1, P_A*P_B^-1, I+P_A*P_B^-1].


    For bg2 the structure of hm_b is given as (for all values of i_ls)
    hm_b =
    [P_A I 0 0
        0 I I 0
        P_B 0 I I
        P_A 0 0 I]
    where P_B and P_A are Shifted identities

    The inverse can be found by solving a linear system of equations
    hm_b_inv =
    [P_B^-1, P_B^-1, P_B^-1, P_B^-1,
        I + P_A*P_B^-1, P_A*P_B^-1, P_A*P_B^-1, P_A*P_B^-1,
        I+P_A*P_B^-1, I+P_A*P_B^-1, P_A*P_B^-1, P_A*P_B^-1,
        P_A*P_B^-1, P_A*P_B^-1, P_A*P_B^-1, I+P_A*P_B^-1]

    Note: the inverse of B is simply a shifted identity matrix with
    negative shift direction.
    """

    # permutation indices
    pm_a = int(bm_b[0, 0])
    if bgn == 1:
        pm_b_inv = int(-bm_b[1, 0])
    else:  # structure of B is slightly different for bg2
        pm_b_inv = int(-bm_b[2, 0])

    hm_b_inv = np.zeros([4 * z, 4 * z])

    im = np.eye(z)

    am = np.roll(im, pm_a, axis=1)
    b_inv = np.roll(im, pm_b_inv, axis=1)
    ab_inv = np.matmul(am, b_inv)

    # row 0
    hm_b_inv[0:z, 0:z] = b_inv
    hm_b_inv[0:z, z : 2 * z] = b_inv
    hm_b_inv[0:z, 2 * z : 3 * z] = b_inv
    hm_b_inv[0:z, 3 * z : 4 * z] = b_inv

    # row 1
    hm_b_inv[z : 2 * z, 0:z] = im + ab_inv
    hm_b_inv[z : 2 * z, z : 2 * z] = ab_inv
    hm_b_inv[z : 2 * z, 2 * z : 3 * z] = ab_inv
    hm_b_inv[z : 2 * z, 3 * z : 4 * z] = ab_inv

    # row 2
    if bgn == 1:
        hm_b_inv[2 * z : 3 * z, 0:z] = ab_inv
        hm_b_inv[2 * z : 3 * z, z : 2 * z] = ab_inv
        hm_b_inv[2 * z : 3 * z, 2 * z : 3 * z] = im + ab_inv
        hm_b_inv[2 * z : 3 * z, 3 * z : 4 * z] = im + ab_inv
    else:  # for bg2 the structure is slightly different
        hm_b_inv[2 * z : 3 * z, 0:z] = im + ab_inv
        hm_b_inv[2 * z : 3 * z, z : 2 * z] = im + ab_inv
        hm_b_inv[2 * z : 3 * z, 2 * z : 3 * z] = ab_inv
        hm_b_inv[2 * z : 3 * z, 3 * z : 4 * z] = ab_inv

    # row 3
    hm_b_inv[3 * z : 4 * z, 0:z] = ab_inv
    hm_b_inv[3 * z : 4 * z, z : 2 * z] = ab_inv
    hm_b_inv[3 * z : 4 * z, 2 * z : 3 * z] = ab_inv
    hm_b_inv[3 * z : 4 * z, 3 * z : 4 * z] = im + ab_inv

    # return results as sparse matrix
    return sp.sparse.csr_matrix(hm_b_inv)


def _encode(
    s: NDArray[np.floating],
    pcm_a: sp.sparse.csr_matrix,
    pcm_b_inv: sp.sparse.csr_matrix,
    pcm_c1: sp.sparse.csr_matrix,
    pcm_c2: sp.sparse.csr_matrix,
) -> NDArray[np.uint8]:
    p_a = pcm_a * s
    p_a = pcm_b_inv * p_a

    p_b_1 = pcm_c1 * s.T
    p_b_2 = pcm_c2 * p_a.T
    p_b = p_b_1 + p_b_2

    c = np.concatenate((s, p_a, p_b)).astype(np.uint8)
    c = np.mod(c, 2)

    N = pcm_c1.shape[0] + pcm_a.shape[1] + pcm_b_inv.shape[0]
    assert c.shape[0] == N

    return c


def _mul_sh(x: NDArray[np.floating], k: int) -> NDArray[np.floating]:
    if k == -1:
        return np.zeros(len(x))
    return np.roll(x, -int(k))


# this is like shown by Prof. Thangaraj in this video
# https://www.youtube.com/watch?v=QJwQi06Fm3M
# this is also how it would be done in hardware
def _encode_thangaraj(B: NDArray[np.float64], Zc: int, msg: NDArray[np.floating]) -> NDArray[np.floating]:
    M, N = B.shape
    cw = np.zeros(N * Zc)
    cw[: (N - M) * Zc] = msg  # it's a systematic code

    temp = np.zeros(Zc, int)
    for i in range(4):
        for j in range(N - M):
            temp = np.mod(temp + _mul_sh(msg[j * Zc :][:Zc], B[i, j]), 2)

    p1_sh = B[1, N - M] if B[2, N - M] == -1 else B[2, N - M]
    cw[(N - M) * Zc :][:Zc] = _mul_sh(temp, Zc - p1_sh)

    # find p2, p3, p4
    for i in range(3):
        temp = np.zeros(Zc, int)
        for j in range(N - M + i + 1):
            temp = np.mod(temp + _mul_sh(cw[j * Zc :][:Zc], B[i, j]), 2)
        cw[(N - M + i + 1) * Zc :][:Zc] = temp

    # remaining parities
    for i in range(4, M):
        temp = np.zeros(Zc, int)
        for j in range(N - M + 4):
            temp = np.mod(temp + _mul_sh(cw[j * Zc :][:Zc], B[i, j]), 2)
        cw[(N - M + i) * Zc :][:Zc] = temp

    return cw


def nrLDPCEncode(
    cbs: NDArray[np.floating], bgn: int, algo: Literal["sionna", "thangaraj"] = "sionna"
) -> NDArray[np.int8]:
    cbs = cbs.copy()  # don't modify inputs

    if algo not in ["sionna", "thangaraj"]:
        raise TypeError('algo has to be "sionna" or "thangaraj"')
    if len(cbs.shape) != 2:
        raise TypeError("cbs must be a 2-dimensional matrix")
    K = cbs.shape[0]  # length of a code segment
    C = cbs.shape[1]  # number of code segments
    if not (11 < K < 8449):
        raise ValueError("K must be 11 < K < 8449")

    # calculate Zc
    if bgn == 1:
        nsys = 22
        ncwnodes = 66
    else:
        nsys = 10
        ncwnodes = 50
    Zc = int(K / nsys)
    assert Zc in getZlist(), f"Zc = {Zc} is not a valid value"

    # calculate output size (N)
    N = int(Zc * ncwnodes)
    codedcbs = np.zeros((N + 2 * Zc, C)).astype(np.int8)

    # find i_ls
    if bgn == 1:
        k_b = 22
    elif bgn == 2:
        if K > 640:
            k_b = 10
        elif K > 560:
            k_b = 9
        elif K > 192:
            k_b = 8
        else:
            k_b = 6
    else:
        raise ValueError(f"bgn = {bgn} is not supported")

    Zarray = getZarray()
    min_val = 100000
    i_ls = None
    for i, s in enumerate(Zarray):
        for s1 in s:
            x = k_b * s1
            if x >= K:
                # valid solution
                if x < min_val:
                    min_val = x
                    i_ls = i
    assert i is not None, "could not find i_ls"
    # print(f'K = {K}, bgn = {bgn} => Zc = {Zc}, k_b = {k_b}, N = {N}, R = {K / N}, i_ls = {i_ls}')

    # replace filler bits with 0
    fill_indices = cbs[:, 0] == -1  # filler bits are at identical locations in every segment
    cbs[fill_indices, :] = 0  # set filler bits to 0

    # encode
    bm = _load_basegraph(i_ls, bgn)

    if algo == "sionna":
        pcm = _lift_basegraph(bm, Zc)
        pcm_a, pcm_b_inv, pcm_c1, pcm_c2 = _gen_submat(bm, k_b, Zc, bgn)
        # print(f'pcm = {pcm.shape[0]} x {pcm.shape[1]} matrix')
        for i in range(cbs.shape[1]):
            codedcbs[:, i] = _encode(cbs[:, i], pcm_a, pcm_b_inv, pcm_c1, pcm_c2)

    elif algo == "thangaraj":
        for i in range(cbs.shape[1]):
            codedcbs[:, i] = _encode_thangaraj(bm, Zc, cbs[:, i])

    # for i in range(cbs.shape[1]):
    #     if not _check_cw(bm, Zc, codedcbs[: , i]):
    #         print(f'Error: cw {i} is not valid')
    #     else:
    #         print(f'cw {i} is valid')

    # set filler bits back to -1
    fill_indices_out = np.append(fill_indices, np.repeat(False, N + 2 * Zc - K))
    codedcbs[fill_indices_out, :] = -1

    # puncture first 2 * Zc systematic bits
    codedcbs = codedcbs[2 * Zc :, :]

    return codedcbs


def _check_cw(B: NDArray[np.float64], Zc: int, cw: NDArray[np.floating]) -> bool:
    M, N = B.shape
    syn = np.zeros(M * Zc)
    for i in range(M):
        for j in range(N):
            syn[i * Zc :][:Zc] = np.mod(syn[i * Zc :][:Zc] + _mul_sh(cw[j * Zc :][:Zc], B[i, j]), 2)
    return not np.any(syn)


if __name__ == "__main__":
    bgn = 2
    C = 2
    K = 2560
    F = 36

    cbs = np.ones((K - F, C))
    cbs[0:10] = 0
    fillers = (-1) * np.ones((F, C))
    cbs = np.vstack((cbs, fillers))
    codedcbs_1 = nrLDPCEncode(cbs.copy(), bgn, algo="sionna")

    codedcbs_2 = nrLDPCEncode(cbs, bgn, algo="thangaraj")

    assert codedcbs_1.shape == (12800, 2)
    assert codedcbs_2.shape == (12800, 2)
    assert np.array_equal(codedcbs_1, codedcbs_2)


def nrLDPCDecode(
    in_: NDArray[np.floating],
    bgn: int,
    maxNumIter: int,
    Algorithm: Literal["Layered belief propagation", "Normalized min-sum", "Offset min-sum"] = (
        "Layered belief propagation"
    ),
    ScalingFactor: float = 0.75,
    Offset: float = 0.5,
    vectorize: bool = True,
    verbose: bool = False,
) -> tuple[NDArray[np.uint8], int]:
    if Algorithm not in ["Layered belief propagation", "Normalized min-sum", "Offset min-sum"]:
        raise ValueError(f"Algorithm {Algorithm} is not supported")
    if len(in_.shape) != 2:
        raise TypeError("cbs must be a 2-dimensional matrix")
    C = in_.shape[1]  # number of code block segments

    if bgn == 1:
        ncwnodes = 66
    else:
        ncwnodes = 50

    N = in_.shape[0]  # length of a code word
    if not (0 < N < (316 * 384) + 1):
        raise ValueError("N = {N} is an unsupported code length")

    Zc = int(N / ncwnodes)
    if not Zc in getZlist():
        raise ValueError(f"Zc = {Zc} is not supported")
    assert Zc == N / ncwnodes, f"N = {N} and ncwnodes = {ncwnodes} is not a valid combination"

    # add punctured 2 * Zc bits
    in_ = np.concatenate((np.zeros((2 * Zc, C)), in_))
    B = in_.shape[0]

    if bgn == 1:
        k_b = 22
    else:
        if B > 640:  # TODO: is it ok to use B instead of N here?
            k_b = 10
        elif B > 560:
            k_b = 9
        elif B > 192:
            k_b = 8
        else:
            k_b = 6
    K = Zc * k_b
    # calulating R = K / B is another possibility and gives a slightly different number,
    # but rate = K / N seems correct, because N is the transmitted number of bits
    rate = K / N

    Zarray = getZarray()
    min_val = 100000
    i_ls = None
    for i, s in enumerate(Zarray):
        for s1 in s:
            x = k_b * s1
            if x >= K:
                # valid solution
                if x < min_val:
                    min_val = x
                    i_ls = i
    assert i is not None, "could not find i_ls"
    if verbose:
        print(
            f"block length B = {in_.shape[0]}, number of information bits K = {K}, code rate R = {rate}, i_ls = {i_ls}"
        )

    bm = _load_basegraph(i_ls, bgn)
    # pcm = _lift_basegraph(bm, Zc)

    Slen = np.sum(bm != -1)
    mb, nb = bm.shape
    rxcbs = np.zeros((K, C), np.uint8)
    if Algorithm == "Layered belief propagation":
        algo = 0
    elif Algorithm == "Normalized min-sum":
        algo = 1
    elif Algorithm == "Offset min-sum":
        algo = 2

    for c_idx in range(C):
        if verbose:
            print(f"decoding segment {c_idx} ...")
        treg = np.zeros((np.max(np.sum(bm != -1, axis=1)), Zc))  # register storage for minsum
        R = np.zeros((Slen, Zc))
        L = in_[:, c_idx]
        itr = 0
        while itr < maxNumIter:
            Ri = 0
            for lyr in range(mb):
                ti = 0  # number of non -1 in row = lyr
                for col in np.where(bm[lyr, :] != -1)[0]:
                    # subtraction
                    L[col * Zc :][:Zc] -= R[Ri, :]
                    # row alignment and store in treg
                    treg[ti, :] = _mul_sh(L[col * Zc :][:Zc], bm[lyr, col])
                    ti += 1
                    Ri += 1
                # minsum on treg
                treg_short = treg[:ti, :]
                if not vectorize:
                    for i1 in range(Zc):
                        pos = np.argmin(np.abs(treg_short[:, i1]))
                        min1 = np.abs(treg_short[pos, i1])  # first minimum
                        temp = np.delete(treg_short[:, i1], pos)
                        min2 = np.min(np.abs(temp))  # second minimum
                        if algo == 1:
                            min1 *= ScalingFactor
                            min2 *= ScalingFactor
                        S = 2 * (treg_short[:, i1] >= 0) - 1
                        parity = np.prod(S)
                        treg_short[:, i1] = min1
                        treg_short[pos, i1] = min2
                        treg_short[:, i1] *= parity * S  # assign signs
                        # print(f'min1 = {min1}, min2 = {min2}, parity = {parity}')
                else:
                    # vectorized version of minsum
                    pos = np.argmin(np.abs(treg_short), axis=0)
                    idx = np.expand_dims(pos, axis=0)
                    min1 = np.take_along_axis(np.abs(treg_short), idx, axis=0)  # first minimum
                    treg_short_2 = treg_short.copy()
                    np.put_along_axis(treg_short_2, idx, np.inf, axis=0)
                    min2 = np.min(np.abs(treg_short_2), axis=0)  # second minimum
                    if algo == 1:
                        min1 *= ScalingFactor
                        min2 *= ScalingFactor
                    S = 2 * (treg_short >= 0) - 1
                    parity = np.prod(S, axis=0)
                    treg_short = np.reshape(np.tile(min1, ti), (ti, Zc))
                    np.put_along_axis(treg_short, idx, min2, axis=0)
                    treg_short *= np.matmul(S, np.diag(parity))

                # column alignment, addition and store in R
                Ri -= ti  # reset the storage counter
                ti = 0
                for col in np.where(bm[lyr, :] != -1)[0]:
                    # column alignment
                    R[Ri, :] = _mul_sh(treg_short[ti, :], Zc - bm[lyr, col])
                    # addition
                    L[col * Zc :][:Zc] += R[Ri, :]
                    Ri += 1
                    ti += 1

            rxcbs[:, c_idx] = np.array(L[:K] < 0).astype(np.uint8)
            itr += 1

    actualniters = itr
    return rxcbs, actualniters


if __name__ == "__main__":
    bgn = 2
    C = 2
    K = 2560
    F = 36
    # cbs = np.ones((K - F, C))
    cbs = np.random.randint(2, size=(K - F, C))
    fillers = (-1) * np.ones((F, C))
    txcbs = np.vstack((cbs, fillers))
    txcodedcbs = nrLDPCEncode(txcbs, bgn)

    # replace filler bits with 0
    fill_indices = txcodedcbs[:, 0] == -1

    # convert to rx soft bits
    rxcodedcbs = 1 - 2 * txcodedcbs.astype(np.double)

    rxcodedcbs[fill_indices, :] = 0

    import time

    import matlab.engine

    _eng = matlab.engine.connect_matlab()
    st = time.time()
    rxcbs2 = _eng.nrLDPCDecode(rxcodedcbs, bgn, 10, "Termination", "max", "Algorithm", "Layered belief propagation")
    et = time.time()
    _eng.quit()
    print(f"decoding with matlab took {et - st} s")

    st = time.time()
    [rxcbs, actualniters] = nrLDPCDecode(rxcodedcbs, bgn, 10, Algorithm="Normalized min-sum", vectorize=True)
    et = time.time()
    txcbs[-F:] = 0
    print(f"decoding with python took {et - st} s")
    assert np.array_equal(rxcbs, txcbs)


def nrRateMatchLDPC(
    in_: NDArray[np.int_], outlen: int, rv: Literal[0, 1, 2, 3], mod: Modulation, nLayers: Literal[1, 2, 3, 4]
) -> NDArray[np.int_]:
    assert rv in [0, 1, 2, 3], "rv has to be in [0, 1, 2, 3]"
    assert nLayers in [1, 2, 3, 4], "nLayers has to be [1, 2, 3, 4]"
    if mod in ["pi/2-BPSK", "BPSK"]:
        Qm = 1
    elif mod == "QPSK":
        Qm = 2
    elif mod == "16QAM":
        Qm = 4
    elif mod == "64QAM":
        Qm = 6
    elif mod == "256QAM":
        Qm = 8
    else:
        assert False, f"modulation type {mod} is not supported"
    N = in_.shape[0]  # length of each code word
    C = in_.shape[1]  # number of code words within this transport block
    Zlist = np.array(getZlist())
    if N in Zlist * 66:
        bgn = 1
        ncwnodes = 66
    elif N in Zlist * 50:
        bgn = 2
        ncwnodes = 50
    else:
        assert False, f"N = {N} is not supported"
    Zc = int(N / ncwnodes)

    Ncb = N

    if bgn == 1:
        if rv == 0:
            k0 = 0
        elif rv == 1:
            k0 = np.floor(17 * Ncb / N) * Zc
        elif rv == 2:
            k0 = np.floor(33 * Ncb / N) * Zc
        elif rv == 3:
            k0 = np.floor(56 * Ncb / N) * Zc
    elif bgn == 2:
        if rv == 0:
            k0 = 0
        elif rv == 1:
            k0 = np.floor(13 * Ncb / N) * Zc
        elif rv == 2:
            k0 = np.floor(25 * Ncb / N) * Zc
        elif rv == 3:
            k0 = np.floor(43 * Ncb / N) * Zc
    k0 = int(k0)
    rematched = np.empty(0, int)
    for i in np.arange(C):
        if i <= C - np.mod(outlen / (nLayers * Qm), C) - 1:
            E = Qm * nLayers * np.floor(outlen / (Qm * nLayers * C)).astype(int)
        else:
            E = Qm * nLayers * np.ceil(outlen / (Qm * nLayers * C)).astype(int)
        rematched = np.append(rematched, _rateMatch(in_[:, [i]], E, k0, Ncb, Qm))

    return rematched


def _rateMatch(d: NDArray[np.int_], E: int, k0: int, Ncb: int, Qm: int) -> NDArray[np.int_]:
    # E is number of bits after rate matching
    N_filler_bits = np.count_nonzero(d[:Ncb, 0] == -1, axis=0)

    d = np.tile(d, (np.ceil(E / (Ncb - N_filler_bits)).astype(int), 1))

    d = np.roll(d, -k0, axis=0)

    e = d[d[:, 0] != -1, :][:E]

    # last bits of QAM modulates symbols are not as reliable as first ones
    # therefore map systematic bits to to first bits of each symbol
    # according to section 5.4.2.2
    e = np.reshape(e, (Qm, int(E / Qm), -1)).ravel(order="F")
    return e


if __name__ == "__main__":
    rv = 0
    mod = "QPSK"
    nLayers = 1
    outlen = 8000
    in_ = np.ones((3960, 2))
    rematched = nrRateMatchLDPC(in_, outlen, rv, mod, nLayers)
    assert rematched.shape == (8000,)


def nrRateRecoverLDPC(
    in_: NDArray[np.floating],
    trblklen: int,
    R: float,
    rv: Literal[0, 1, 2, 3],
    mod: Modulation,
    nLayers: int,
    numCB: int | None = None,
) -> NDArray[np.floating]:
    assert (R > 0) and (R < 1), "R has to be 0 < R < 1"
    assert rv in [0, 1, 2, 3], "rv has to be in [0, 1, 2, 3]"

    if mod in ["pi/2-BPSK", "BPSK"]:
        Qm = 1
    elif mod == "QPSK":
        Qm = 2
    elif mod == "16QAM":
        Qm = 4
    elif mod == "64QAM":
        Qm = 6
    elif mod == "256QAM":
        Qm = 8
    else:
        assert False, f"modulation type {mod} is not supported"

    cbsinfo = nrDLSCHInfo(trblklen, R)
    bgn = cbsinfo["BGN"]
    Zc = cbsinfo["Zc"]
    N = cbsinfo["N"]

    C = cbsinfo["C"] if numCB is None else numCB
    Ncb = N

    if bgn == 1:
        if rv == 0:
            k0 = 0
        elif rv == 1:
            k0 = np.floor(17 * Ncb / N) * Zc
        elif rv == 2:
            k0 = np.floor(33 * Ncb / N) * Zc
        elif rv == 3:
            k0 = np.floor(56 * Ncb / N) * Zc
    elif bgn == 2:
        if rv == 0:
            k0 = 0
        elif rv == 1:
            k0 = np.floor(13 * Ncb / N) * Zc
        elif rv == 2:
            k0 = np.floor(25 * Ncb / N) * Zc
        elif rv == 3:
            k0 = np.floor(43 * Ncb / N) * Zc
    k0 = int(k0)

    G = len(in_)
    out = np.zeros((N, C))
    idx = 0
    for r in np.arange(C):
        if r <= C - np.mod(G / (nLayers * Qm), C) - 1:
            E = Qm * nLayers * np.floor(G / (Qm * nLayers * C)).astype(int)
        else:
            E = Qm * nLayers * np.ceil(G / (Qm * nLayers * C)).astype(int)

        # pad unknown bits
        if G < E:
            deconcatenated = np.append(in_, np.zeros(E - G))
        else:
            deconcatenated = in_[idx : idx + E]
        idx += E

        out[:, r] = _rateRecover(deconcatenated, cbsinfo, k0, Ncb, Qm)
    return out


def _rateRecover(
    in_: NDArray[np.floating], cbsinfo: dict[str, int], k0: int, Ncb: int, Qm: int
) -> NDArray[np.floating]:
    # perform deinterleaving according to section 5.4.2.2
    E = len(in_)
    in_ = np.reshape(in_, (int(E / Qm), Qm)).ravel("F")

    # puncture systematic bits and remove fill bits
    K = int(cbsinfo["K"] - 2 * cbsinfo["Zc"])
    Kd = int(K - cbsinfo["F"])

    N_filler_bits = int(np.min((K, Ncb)) - Kd)

    N_buffer = Ncb - N_filler_bits
    idx = np.tile(np.arange(Ncb), np.ceil(E / N_buffer).astype(int))

    idx = np.roll(idx, -k0)

    indices = np.delete(idx, (idx >= Kd) & (idx < K))
    indices = indices[:E]

    out = np.zeros(cbsinfo["N"])
    out[Kd:K] = np.inf

    if E > N_buffer:
        for i in np.arange(np.floor(E / N_buffer).astype(int)):
            out[indices[:N_buffer]] += in_[i * N_buffer : (i + 1) * N_buffer]

        rem_bits = np.mod(E, N_buffer)
        out[indices[:rem_bits]] += in_[-rem_bits:]

    else:
        out[indices] = in_

    return out


if __name__ == "__main__":
    sbits = np.ones(4500)
    trblklen = 4000
    R = 0.5
    rv = 1
    mod = "QPSK"
    nLayers = 1
    numCB = 1
    raterec = nrRateRecoverLDPC(sbits, trblklen, R, rv, mod, nLayers, numCB)
    print(raterec.shape)
