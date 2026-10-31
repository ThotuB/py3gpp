import matlab.engine
import pytest
from matlab.engine.matlabengine import MatlabEngine


@pytest.fixture(scope="session")
def eng():
    eng = matlab.engine.connect_matlab()
    assert isinstance(eng, MatlabEngine)
    return eng
