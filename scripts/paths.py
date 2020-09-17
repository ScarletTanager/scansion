import sys
from os import path

OUR_PATHS = [
    'model'
]


def add_repo_paths():
    this_dir = path.dirname(path.realpath(__file__))
    for p in OUR_PATHS:
        sys.path.append(path.join(this_dir, '..', p))
