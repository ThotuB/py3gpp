from __future__ import annotations

from typing import Any

from py3gpp.dl.ch.trs.dlsch import getBGNInfo, getCBSInfo


def nrULSCHInfo(tbs: int | None, tcr: float) -> dict[str, Any]:
    """Get uplink shared channel (UL-SCH) information."""
    # TS 38.212 6.2 (UL-SCH) reuses the same base-graph-selection (5.2.2) and code-block-
    # segmentation (5.3.2) clauses as DL-SCH (38.212 7.2) -- the math is identical, only the
    # transport channel name differs, so this reuses nrDLSCHInfo's helpers directly.
    assert tbs is None or tbs >= 0
    assert tbs is None or type(tbs) == int
    assert tcr > 0 and tcr < 1

    bg_info = getBGNInfo(0 if tbs is None else tbs, tcr)
    cb_info = getCBSInfo(bg_info["B"], bg_info["BGN"])

    if bg_info["BGN"] == 1:
        N = 66 * cb_info["Zc"]
    else:
        N = 50 * cb_info["Zc"]

    info = dict()
    info["CRC"] = bg_info["CRC"]
    info["L"] = bg_info["L"]
    info["BGN"] = bg_info["BGN"]
    info["C"] = cb_info["C"]
    info["Lcb"] = cb_info["Lcb"]
    info["F"] = cb_info["F"]
    info["Zc"] = cb_info["Zc"]
    info["K"] = cb_info["K"]
    info["N"] = N

    if tbs is None:
        info["L"] = 0
        info["F"] = 0
        info["Zc"] = 2
        info["K"] = 0
        info["N"] = 0

    return info
