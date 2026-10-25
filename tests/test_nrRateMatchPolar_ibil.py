import numpy as np

from py3gpp import nrRateMatchPolar, nrRateRecoverPolar


def test_nrRateMatchPolar_ibil_round_trip():
    # TS 38.212 5.4.1.3 triangular (uplink-only) coded-bit interleaver round trip:
    # encode -> perfect-channel LLRs -> recover must reproduce the original Polar codeword.
    rng = np.random.default_rng(1)
    N = 32
    K = 18

    for E in [32, 40, 60, 100]:
        enc = rng.integers(0, 2, N)
        y = nrRateMatchPolar(enc, K, E, ibil=True)
        assert y.shape == (E,)

        llr = 1 - 2.0 * y  # perfect channel: bit 0 -> +1, bit 1 -> -1
        recovered = nrRateRecoverPolar(llr, K, N, ibil=True, discardRepetition=False)
        recoveredBits = (recovered < 0).astype(int)
        assert np.array_equal(recoveredBits, enc)


def test_nrRateMatchPolar_ibil_differs_from_no_interleaving():
    rng = np.random.default_rng(2)
    enc = rng.integers(0, 2, 32)
    K, E = 18, 60

    withIbil = nrRateMatchPolar(enc, K, E, ibil=True)
    withoutIbil = nrRateMatchPolar(enc, K, E, ibil=False)
    assert not np.array_equal(withIbil, withoutIbil)
