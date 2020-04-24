import pathlib
import os.path
from functools import lru_cache


@lru_cache(1)
def news_api_key():
    file_dir = pathlib.Path(__file__).parent.absolute()
    base_dir = os.path.dirname(file_dir)
    with open(os.path.join(base_dir, 'secrets/news_api_key')) as f:
        return f.read()
