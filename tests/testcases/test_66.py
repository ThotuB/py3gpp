from py3gpp import nrCarrierConfig, nrPDSCHConfig, nrPDSCHDMRSIndices


def test_issue_66():
    cfg = nrPDSCHConfig()
    carrier = nrCarrierConfig()
    dmrsIndices = nrPDSCHDMRSIndices(carrier, cfg)
