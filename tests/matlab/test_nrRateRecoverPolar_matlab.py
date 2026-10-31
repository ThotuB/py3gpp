import itertools

import matlab.engine
import numpy as np
import pytest

from py3gpp.plc.trs.polar import nrRateRecoverPolar


def run_nrRateRecoverPolar(N, eng):
    K = 56
    cw = np.arange(N)
    ref_data = eng.nrRateRecoverPolar(eng.transpose(eng.double(cw)), eng.double(K), eng.double(N))
    ref_data = np.array(list(itertools.chain(*ref_data)))

    data = nrRateRecoverPolar(cw, K, N, False)

    assert (ref_data == data).all()


@pytest.mark.parametrize("N", [512, 256, 128])
def test_nrRateRecoverPolar_matlab(N, eng):
    run_nrRateRecoverPolar(N, eng)
