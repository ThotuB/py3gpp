import os

import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrPDSCHConfig, nrPDSCHIndices, nrPDSCHReservedConfig


def run_nr_pdschindices_reserved(cfg, eng, expect_exclusion=None):
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = cfg["SubcarrierSpacing"]
    carrier.NSizeGrid = cfg["NSizeGrid"]
    carrier.NStartGrid = cfg["NStartGrid"]
    carrier.NSlot = cfg["NSlot"]

    pdsch = nrPDSCHConfig()
    pdsch.PRBSet = cfg["PRBSet"]
    pdsch.SymbolAllocation = cfg["SymbolAllocation"]
    pdsch.DMRS.DMRSTypeAPosition = cfg["DMRSTypeAPosition"]
    pdsch.DMRS.DMRSAdditionalPosition = cfg["DMRSAdditionalPosition"]
    pdsch.DMRS.DMRSConfigurationType = cfg["DMRSConfigurationType"]

    rsv = nrPDSCHReservedConfig()
    rsv.PRBSet = cfg["ReservedPRBSet"]
    rsv.SymbolSet = cfg["ReservedSymbolSet"]
    if cfg["ReservedPeriod"] > 0:
        rsv.Period = cfg["ReservedPeriod"]
    pdsch.ReservedPRB = [rsv]

    ind = nrPDSCHIndices(carrier, pdsch)

    ind_ref = eng.gen_pdschindices_reserved(cfg)
    ind_ref = np.asarray(ind_ref).ravel().astype(int) - 1

    assert ind.shape == ind_ref.shape
    assert np.array_equal(np.sort(ind), np.sort(ind_ref))

    if expect_exclusion is not None:
        pdsch.ReservedPRB = []
        unreserved = nrPDSCHIndices(carrier, pdsch)
        if expect_exclusion:
            assert ind.shape != unreserved.shape, "reservation was expected to exclude some REs, but didn't"
        else:
            assert ind.shape == unreserved.shape, "reservation was expected to be a no-op, but wasn't"


def _base_cfg():
    return {
        "SubcarrierSpacing": 30,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        # NSlot=0 so that an unperiodic SymbolSet given in local 0..SymbolsPerSlot-1 terms lines
        # up and actually applies -- see test_nr_pdschindices_reserved_periodic_matlab for the
        # NSlot/Period interaction itself.
        "NSlot": 0,
        "PRBSet": list(range(52)),
        "SymbolAllocation": [0, 14],
        "DMRSTypeAPosition": 2,
        "DMRSAdditionalPosition": 0,
        "DMRSConfigurationType": 1,
        "ReservedPRBSet": [],
        "ReservedSymbolSet": [],
        "ReservedPeriod": 0,
    }


def test_nr_pdschindices_reserved_no_reservation_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    run_nr_pdschindices_reserved(_base_cfg(), eng)


def test_nr_pdschindices_reserved_simple_matlab(eng):
    # A reservation covering every symbol but only a handful of PRBs (mimics an SSB-shaped
    # frequency-only exclusion within the PDSCH allocation).
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["ReservedPRBSet"] = list(range(10, 15))
    cfg["ReservedSymbolSet"] = list(range(14))
    run_nr_pdschindices_reserved(cfg, eng, expect_exclusion=True)


def test_nr_pdschindices_reserved_symbol_subset_matlab(eng):
    # A reservation that only covers a subset of OFDM symbols (mimics an SSB-shaped exclusion:
    # reserved in time AND frequency, not just frequency).
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["ReservedPRBSet"] = list(range(20, 40))
    cfg["ReservedSymbolSet"] = [2, 3, 4, 5]
    run_nr_pdschindices_reserved(cfg, eng, expect_exclusion=True)


def test_nr_pdschindices_reserved_nonzero_symstart_matlab(eng):
    # Combine with a non-default (non-zero) symStart allocation, to make sure the two fixes
    # (symStart handling + ReservedPRB) compose correctly.
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["SymbolAllocation"] = [2, 12]
    cfg["ReservedPRBSet"] = list(range(0, 10))
    cfg["ReservedSymbolSet"] = list(range(2, 14))
    run_nr_pdschindices_reserved(cfg, eng, expect_exclusion=True)


@pytest.mark.parametrize(
    "nslot,period,expect_exclusion",
    [(4, 2, True), (5, 2, False), (0, None, True)],
    ids=["nslot_mod_period_is_0", "nslot_mod_period_is_1", "no_period_at_nslot_0"],
)
def test_nr_pdschindices_reserved_periodic_matlab(nslot, period, expect_exclusion, eng):
    # The reservation's SymbolSet/Period together project onto the CURRENT slot's local symbol
    # range via (nslot % Period); only slots where that offset is 0 see the pattern apply.
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["NSlot"] = nslot
    cfg["ReservedPRBSet"] = list(range(5, 15))
    cfg["ReservedSymbolSet"] = list(range(14))
    cfg["ReservedPeriod"] = period or 0
    run_nr_pdschindices_reserved(cfg, eng, expect_exclusion=expect_exclusion)


def test_nr_pdschindices_reserved_outside_prbset_is_noop_matlab(eng):
    # A reservation whose PRBSet doesn't intersect the channel's own PRBSet should change nothing.
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["PRBSet"] = list(range(20))
    cfg["ReservedPRBSet"] = list(range(30, 40))
    cfg["ReservedSymbolSet"] = list(range(14))
    run_nr_pdschindices_reserved(cfg, eng, expect_exclusion=False)
