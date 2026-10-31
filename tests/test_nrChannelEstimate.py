import numpy as np

from py3gpp import nrChannelEstimate


def test_nvar_single_frontloaded_dmrs_symbol():
    # Regression test: nrChannelEstimate's nVar estimate used to hardcode grid columns 1 and 3
    # (assuming a 2-symbol DM-RS pattern) -- silently collapsing to ~0 for any other layout, such
    # as this single front-loaded DM-RS symbol at column 2. Verify the fix recovers a known
    # injected noise variance regardless of which column(s) actually carry pilots.
    rng = np.random.default_rng(0)

    K, N = 624, 14  # 52 PRBs * 12 subcarriers, 14 OFDM symbols
    dmrs_symbol = 2
    pilot_subcarriers = np.arange(0, K, 2)  # comb-2 pattern
    refInd = pilot_subcarriers + dmrs_symbol * K  # column-major flat indices

    qpsk = np.array([1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j]) / np.sqrt(2)
    refSym = qpsk[rng.integers(0, 4, len(pilot_subcarriers))]

    true_nvar = 0.02
    noise = np.sqrt(true_nvar / 2) * (
        rng.standard_normal(len(pilot_subcarriers)) + 1j * rng.standard_normal(len(pilot_subcarriers))
    )
    # Flat (unity) true channel isolates the noise estimate from any channel-smoothness effects.
    noisy_pilots = refSym + noise

    rxGrid = np.zeros((K, N), dtype=complex)
    rxGrid[pilot_subcarriers, dmrs_symbol] = noisy_pilots

    result = nrChannelEstimate(rxGrid, refInd, refSym)
    assert result is not None
    _, nVar = result

    assert nVar > 0, "nVar must not collapse to ~0 for a single-DM-RS-symbol layout"
    assert abs(nVar - true_nvar) / true_nvar < 0.3


def test_nvar_two_symbol_dmrs_pattern():
    # Same check for a 2-symbol DM-RS pattern (the layout the old hardcoded implementation was
    # implicitly tuned for), to confirm the general fix still works there too.
    rng = np.random.default_rng(1)

    K, N = 624, 14
    dmrs_symbols = [1, 3]
    pilot_subcarriers = np.arange(0, K, 2)

    qpsk = np.array([1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j]) / np.sqrt(2)
    true_nvar = 0.01

    rxGrid = np.zeros((K, N), dtype=complex)
    refInd_list = []
    refSym_list = []
    for sym in dmrs_symbols:
        refSym = qpsk[rng.integers(0, 4, len(pilot_subcarriers))]
        noise = np.sqrt(true_nvar / 2) * (
            rng.standard_normal(len(pilot_subcarriers)) + 1j * rng.standard_normal(len(pilot_subcarriers))
        )
        rxGrid[pilot_subcarriers, sym] = refSym + noise
        refInd_list.append(pilot_subcarriers + sym * K)
        refSym_list.append(refSym)

    refInd = np.concatenate(refInd_list)
    refSym = np.concatenate(refSym_list)

    result = nrChannelEstimate(rxGrid, refInd, refSym)
    assert result is not None
    _, nVar = result

    assert abs(nVar - true_nvar) / true_nvar < 0.3
