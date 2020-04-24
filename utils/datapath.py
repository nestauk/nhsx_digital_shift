'''
datapath
========

Get full file path to data directories. This assumes
that the top data directory is {down one, up one}
from the path to this file (datapath.py)
'''

import pathlib
import os.path
from functools import lru_cache


@lru_cache(5)
def _datapath(data_dirname):
    '''Helper function for evaluating the full path to the data directories.'''
    file_dir = pathlib.Path(__file__).parent.absolute()
    base_dir = os.path.dirname(file_dir)
    data_dir = os.path.join(base_dir, 'data')
    full_path = os.path.join(data_dir, data_dirname)
    if not os.path.exists(full_path):
        raise OSError(f'Directory {full_path} does not exist')
    return full_path


def datapath(data_dirname, filename):
    '''Generate the full path to a hypothetical data file.

    Args:
        data_dirname (str): One of the subdirectories of the /data/ directory.
        filename (str): A file name to append to the end of the full path to :obj:`data_dirname`
    Returns:
        full_path (str): :obj:`/full/path/to/data/data_dirname/filename`
    '''
    full_path = _datapath(data_dirname)
    return os.path.join(full_path, filename)
