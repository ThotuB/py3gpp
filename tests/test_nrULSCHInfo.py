from py3gpp import nrDLSCHInfo, nrULSCHInfo


def test_nrULSCHInfo():
    R = 449 / 1024
    A = 50
    ulsch_info = nrULSCHInfo(A, R)
    assert ulsch_info["F"] == 44


def test_nrULSCHInfo_matches_nrDLSCHInfo():
    # TS 38.212 6.2 (UL-SCH) reuses the exact same base-graph-selection/code-block-segmentation
    # math as DL-SCH (38.212 7.2) -- confirms the two stay in sync across a range of inputs.
    for tbs, tcr in [(50, 449 / 1024), (3000, 0.5), (8000, 0.8), (None, 0.5)]:
        assert nrULSCHInfo(tbs, tcr) == nrDLSCHInfo(tbs, tcr)
