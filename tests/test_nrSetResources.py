import numpy as np

from py3gpp import (
    nrCarrierConfig,
    nrCSIRS,
    nrCSIRSConfig,
    nrCSIRSIndices,
    nrExtractResources,
    nrResourceGrid,
    nrSetResources,
)


def test_2d_grid_write_still_works():
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52

    grid = nrResourceGrid(carrier, p=1)
    ind = np.array([0, 1, 624, 625])  # two REs in symbol 0, two in symbol 1 (624 = 12*52)
    vals = np.array([1 + 1j, 2 + 2j, 3 + 3j, 4 + 4j])

    nrSetResources(ind, grid, vals)

    assert grid[0, 0] == vals[0]
    assert grid[1, 0] == vals[1]
    assert grid[0, 1] == vals[2]
    assert grid[1, 1] == vals[3]


def test_3d_grid_multiport_write():
    # Regression test: nrSetResources used to only ever index 2 dimensions, so for a 3D
    # multi-port grid, any port >= 1's indices (which start beyond nSC*nSym) never matched
    # and were silently dropped -- the port's REs simply never got written, no error.
    carrier = nrCarrierConfig()
    carrier.NSizeGrid = 52

    csirs = nrCSIRSConfig()
    csirs.RowNumber = 3  # 2-port, fd-CDM2
    csirs.SubcarrierLocations = 0
    csirs.SymbolLocations = 5

    ind = nrCSIRSIndices(carrier, csirs)
    sym = nrCSIRS(carrier, csirs)

    grid = nrResourceGrid(carrier, p=2)
    nrSetResources(ind, grid, sym)

    nSC, nSym = grid.shape[0], grid.shape[1]
    totalSC = nSC
    port_stride = nSC * nSym
    port0_ind = ind[ind < port_stride]
    port1_ind = ind[ind >= port_stride] - port_stride

    # Port 0's REs actually landed in grid[:, :, 0], and are nonzero.
    for i in port0_ind:
        sc, symIdx = i % totalSC, i // totalSC
        assert grid[sc, symIdx, 0] != 0

    # Port 1's REs actually landed in grid[:, :, 1] (this is exactly what was silently dropped
    # before the fix), and are nonzero.
    for i in port1_ind:
        sc, symIdx = i % totalSC, i // totalSC
        assert grid[sc, symIdx, 1] != 0

    # The two ports carry different values (fd-CDM2 OCC: port0 and port1 differ in sign on the
    # second subcarrier of each pair), confirming they weren't both written with the same data.
    extracted = nrExtractResources(ind, grid)
    assert not np.array_equal(extracted[: len(port0_ind)], extracted[len(port0_ind) :])
