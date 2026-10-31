import itertools

import matlab.engine
from matlab.engine.matlabengine import MatlabEngine
import numpy as np
import pytest

from py3gpp.dl.ch.trs.dlsch import nrDLSCHInfo


def run_nr_dlsch_info(tbs, tcr, eng):
    ref_data = eng.nrDLSCHInfo(matlab.double(tbs), matlab.double(tcr))
    # print(ref_data)

    data = nrDLSCHInfo(tbs, tcr)

    assert np.all(ref_data == data)


@pytest.fixture(scope="session")
def eng():
    eng = matlab.engine.connect_matlab()
    assert isinstance(eng, MatlabEngine)
    yield eng
    eng.quit()


@pytest.mark.parametrize("tbs", [0, 1, 100, 3824, 6666])
@pytest.mark.parametrize("tcr", [0.1, 0.25, 0.67, 0.99])
def test_nr_dlsch_info_matlab(tbs, tcr, eng):
    run_nr_dlsch_info(tbs, tcr, eng)
