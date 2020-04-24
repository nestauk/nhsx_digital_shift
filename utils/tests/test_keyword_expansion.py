from utils.keyword_expansion import matrix_fraction
from utils.keyword_expansion import jlh

import numpy as np
import pytest


def frac(top, bottom):
    return pytest.approx(top/bottom)


@pytest.fixture
def a():
    return np.array([[1, 1, 2], [0, 0, 2]])


@pytest.fixture
def b():
    return np.array([[1, 2, 2], [1, 0, 2]])


def test_matrix_fraction(a, b):
    assert matrix_fraction(a).tolist() == [frac(1, 6), frac(1, 6), frac(4, 6)]
    assert matrix_fraction(b).tolist() == [frac(2, 8), frac(2, 8), frac(4, 8)]


def test_jlh(a, b):
    assert jlh(a, b) == [frac(-8, 144), frac(-8, 144), frac(32, 144)]
