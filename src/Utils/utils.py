import json 
import os
import sys

def get_config(path:str, verbose:bool = False):
    with open(path, 'r') as f:
        config = json.load(f)
    if verbose:
        print(f'Loaded config from {path}')
    return config

def dump_config(config:dict, path:str, verbose:bool = False):
    with open(path, 'w') as f:
        json.dump(config, f, indent=4)
    if verbose:
        print(f'Dumped config to {path}')
