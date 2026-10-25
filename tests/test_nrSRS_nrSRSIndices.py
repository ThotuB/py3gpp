import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrSRS, nrSRSConfig, nrSRSIndices


def _basicSrs():
    srs = nrSRSConfig()
    srs.NumSRSPorts = 2
    srs.NumSRSSymbols = 4
    srs.SymbolStart = 8
    srs.CSRS = 5
    srs.BSRS = 0
    return srs


def test_nrSRS_nrSRSIndices_matches_matlab_docstring_example():
    # Reference values captured from a live MATLAB 5G Toolbox (R2026a) session running
    # nrSRS.m's own documented example (carrier/srs defaults plus the shown overrides).
    carrier = nrCarrierConfig()
    srs = _basicSrs()

    sym, info = nrSRS(carrier, srs)
    ind = nrSRSIndices(carrier, srs)

    assert sym.shape == ind.shape == (960,)
    assert info["SeqLength"] == 120

    Msc, NSym, NPorts = info["SeqLength"], srs.NumSRSSymbols, srs.NumSRSPorts
    sym2d = sym.reshape(NPorts, Msc * NSym).T
    ind2d = ind.reshape(NPorts, Msc * NSym).T

    assert np.allclose(sym2d[0, 0], 1 + 0j, atol=1e-8)
    assert np.allclose(sym2d[1, 0], 0.97536788 - 0.22058445j, atol=1e-6)
    assert np.allclose(sym2d[0, 1], 1 + 0j, atol=1e-8)
    assert np.allclose(sym2d[1, 1], -0.97536788 + 0.22058445j, atol=1e-6)

    assert ind2d[0, 0] == 4992  # MATLAB 1-based 4993, minus 1
    assert ind2d[0, 1] == 13728  # MATLAB 1-based 13729, minus 1


def test_nrSRS_structural_properties():
    carrier = nrCarrierConfig()
    srs = _basicSrs()

    sym, info = nrSRS(carrier, srs)
    ind = nrSRSIndices(carrier, srs)

    assert np.allclose(np.abs(sym), 1.0)  # unit-magnitude low-PAPR sequence
    assert len(np.unique(ind)) == ind.size  # no duplicate REs across ports/symbols/subcarriers
    assert ind.min() >= 0
    assert ind.max() < carrier.NSizeGrid * 12 * carrier.SymbolsPerSlot * srs.NumSRSPorts


def test_nrSRS_port_cyclic_shift_relationship():
    # Port p's sequence must equal port 0's sequence times exp(j*(alpha_p - alpha_0)*n),
    # directly encoding TS 38.211's cyclic-shift definition -- a property check that doesn't
    # need an external reference.
    carrier = nrCarrierConfig()
    srs = nrSRSConfig()
    srs.NumSRSPorts = 4
    srs.NumSRSSymbols = 1
    srs.SymbolStart = 10
    srs.CSRS = 10
    srs.CyclicShift = 2

    sym, info = nrSRS(carrier, srs)
    Msc = info["SeqLength"]
    sym2d = sym.reshape(srs.NumSRSPorts, Msc).T
    alpha = info["Alpha"]

    n = np.arange(Msc)
    for p in range(1, srs.NumSRSPorts):
        expected = sym2d[:, 0] * np.exp(1j * n * (alpha[p] - alpha[0]))
        assert np.allclose(sym2d[:, p], expected, atol=1e-8)


def test_nrSRS_inactive_slot_returns_empty():
    carrier = nrCarrierConfig()
    srs = _basicSrs()
    srs.SRSPeriod = "off"

    sym, info = nrSRS(carrier, srs)
    ind = nrSRSIndices(carrier, srs)
    assert sym.shape == (0,)
    assert ind.shape == (0,)
    assert info["SeqLength"] == 0


def test_nrSRS_periodic_candidate_slots():
    carrier = nrCarrierConfig()
    srs = _basicSrs()
    srs.SRSPeriod = [4, 1]  # periodicity 4 slots, offset 1

    active = []
    for slot in range(8):
        carrier.NSlot = slot
        sym, _ = nrSRS(carrier, srs)
        active.append(sym.shape != (0,))
    assert active == [False, True, False, False, False, True, False, False]


@pytest.mark.parametrize(
    "setup",
    [
        lambda srs: setattr(srs, "BHop", 0) or setattr(srs, "BSRS", 1),
        lambda srs: setattr(srs, "GroupSeqHopping", "groupHopping"),
        lambda srs: setattr(srs, "EnableEightPortTDM", True),
        lambda srs: setattr(srs, "CombOffsetHopping", True),
        lambda srs: setattr(srs, "CyclicShiftHopping", True),
        lambda srs: setattr(srs, "SRSPositioning", True),
        lambda srs: setattr(srs, "FrequencyScalingFactor", 2),
    ],
)
def test_nrSRS_unsupported_features_raise_not_implemented(setup):
    carrier = nrCarrierConfig()
    srs = _basicSrs()
    setup(srs)

    with pytest.raises(NotImplementedError):
        nrSRS(carrier, srs)
    with pytest.raises(NotImplementedError):
        nrSRSIndices(carrier, srs)
