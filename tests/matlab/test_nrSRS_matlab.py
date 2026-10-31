import os

import matlab.engine
import numpy as np
import pytest

from py3gpp import nrCarrierConfig, nrSRS, nrSRSConfig, nrSRSIndices


def run_nr_srs(cfg, eng):
    carrier = nrCarrierConfig()
    carrier.SubcarrierSpacing = cfg["SubcarrierSpacing"]
    carrier.NSizeGrid = cfg["NSizeGrid"]
    carrier.NStartGrid = cfg["NStartGrid"]
    carrier.NSlot = cfg["NSlot"]

    srs = nrSRSConfig()
    srs.NumSRSPorts = cfg["NumSRSPorts"]
    srs.NumSRSSymbols = cfg["NumSRSSymbols"]
    srs.SymbolStart = cfg["SymbolStart"]
    srs.CSRS = cfg["CSRS"]
    srs.BSRS = cfg["BSRS"]
    srs.KTC = cfg["KTC"]
    srs.KBarTC = cfg["KBarTC"]
    srs.CyclicShift = cfg["CyclicShift"]
    srs.FrequencyStart = cfg["FrequencyStart"]
    srs.NRRC = cfg["NRRC"]
    srs.SRSPeriod = cfg["SRSPeriod"]

    sym, _ = nrSRS(carrier, srs)
    ind = nrSRSIndices(carrier, srs)

    sym_ref, ind_ref = eng.gen_srs(cfg, nargout=2)
    # MATLAB's nrSRS/nrSRSIndices return an (Msc*NSym) x NumSRSPorts matrix; flatten
    # column-major (port-major) to match py3gpp's established flat-array convention.
    sym_ref = np.asarray(sym_ref).ravel(order="F")
    ind_ref = np.asarray(ind_ref).ravel(order="F").astype(int) - 1

    assert sym.shape == sym_ref.shape
    assert np.allclose(sym, sym_ref, atol=1e-6)
    assert ind.shape == ind_ref.shape
    assert np.array_equal(ind, ind_ref)


def _base_cfg():
    return {
        "SubcarrierSpacing": 15,
        "NSizeGrid": 52,
        "NStartGrid": 0,
        "NSlot": 0,
        "NumSRSPorts": 2,
        "NumSRSSymbols": 4,
        "SymbolStart": 8,
        "CSRS": 5,
        "BSRS": 0,
        "KTC": 2,
        "KBarTC": 0,
        "CyclicShift": 0,
        "FrequencyStart": 0,
        "NRRC": 0,
        "SRSPeriod": "on",
    }


def test_nr_srs_2port_comb2_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    run_nr_srs(_base_cfg(), eng)


def test_nr_srs_4port_comb4_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["NumSRSPorts"] = 4
    cfg["NumSRSSymbols"] = 1
    cfg["SymbolStart"] = 10
    cfg["CSRS"] = 10
    cfg["KTC"] = 4
    cfg["CyclicShift"] = 2
    cfg["FrequencyStart"] = 3
    cfg["NRRC"] = 2
    run_nr_srs(cfg, eng)


@pytest.mark.parametrize("num_ports", [1, 2, 4])
@pytest.mark.parametrize("ktc", [2, 4])
def test_nr_srs_port_comb_sweep_matlab(num_ports, ktc, eng):
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["NumSRSPorts"] = num_ports
    cfg["KTC"] = ktc
    run_nr_srs(cfg, eng)


def test_nr_srs_periodic_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["SRSPeriod"] = [4, 1]
    run_nr_srs(cfg, eng)


def test_nr_srs_inactive_slot_matlab(eng):
    eng.cd(os.path.dirname(__file__))
    cfg = _base_cfg()
    cfg["SRSPeriod"] = "off"
    run_nr_srs(cfg, eng)
