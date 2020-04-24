import pytest
from unittest import mock
import os

from utils.datapath import _datapath
from utils.datapath import datapath


def test__datapath_path_exists():
    for data_dirname in ['raw', 'processed', 'outputs']:
        the_datapath = _datapath(data_dirname)
        prefix, suffix = os.path.split(the_datapath)
        assert suffix == data_dirname


def test__datapath_path_not_exists():
    for data_dirname in ['a', 'b', 'c']:
        with pytest.raises(OSError):
            _datapath(data_dirname)


def test_datapath_exists():
    for data_dirname in ['raw', 'processed', 'outputs']:
        for filename in ['blah.json', 'something.csv', 'else.xml']:
            filepath = datapath(data_dirname, filename)
            prefix, suffix = os.path.split(filepath)
            assert suffix == filename


def test_datapath_exists():
    for data_dirname in ['a', 'b', 'c']:
        for filename in ['blah.json', 'something.csv', 'else.xml']:
            with pytest.raises(OSError):
                datapath(data_dirname, filename)
