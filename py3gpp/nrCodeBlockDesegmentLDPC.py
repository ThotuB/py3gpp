from __future__ import annotations

from typing import Literal

import numpy as np
from numpy.typing import NDArray

from py3gpp.nrCRCDecode import nrCRCDecode
from py3gpp.nrDLSCHInfo import getCBSInfo


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
