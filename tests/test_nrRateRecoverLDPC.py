import numpy as np
import test_data.ldpc

from py3gpp.transport_channel_subcomponents.nrRateRecoverLDPC import nrRateRecoverLDPC


def test_nrRateRecoverLDPC():
    # test data from SIB1 decoding with Matlab
    rv = 0
    mod = "QPSK"
    nLayers = 1
    trblklen = 640
    R = 0.3701
    raterec = nrRateRecoverLDPC(test_data.ldpc.cw, trblklen, R, rv, mod, nLayers)
    assert np.array_equal(raterec[:, 0], test_data.ldpc.raterec)


if __name__ == "__main__":
    test_nrRateRecoverLDPC()
