import pytest

from py3gpp import nrCarrierConfig, nrPRACHConfig, nrPRACHOFDMInfo


def test_nrPRACHOFDMInfo_matches_matlab_reference():
    # Reference values captured from a live MATLAB 5G Toolbox (R2026a) session:
    #   carrier = nrCarrierConfig; prach = nrPRACHConfig;  % Format 0, defaults
    #   info = nrPRACHOFDMInfo(carrier, prach);
    #   info.Nfft == 12288, info.SampleRate == 15360000, info.CyclicPrefixLengths == 1584,
    #   info.GuardLengths == 1488, info.SymbolLengths == 15360, info.Windowing == 430
    carrier = nrCarrierConfig()
    prach = nrPRACHConfig()

    info = nrPRACHOFDMInfo(carrier, prach)

    assert info["Nfft"] == 12288
    assert info["SampleRate"] == 15360000
    assert info["CyclicPrefixLengths"] == 1584
    assert info["GuardLengths"] == 1488
    assert info["SymbolLengths"] == 15360
    assert info["OffsetLength"] == 0
    assert info["Windowing"] == 430


def test_nrPRACHOFDMInfo_only_format0_supported():
    carrier = nrCarrierConfig()
    prach = nrPRACHConfig()
    prach.ConfigurationIndex = 28  # Format 1
    with pytest.raises(NotImplementedError):
        nrPRACHOFDMInfo(carrier, prach)
