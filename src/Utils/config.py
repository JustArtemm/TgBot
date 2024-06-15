import os, sys, json
import Utils.utils as uu

class BaseConfig():
    """
    Base configuration class.
    """
    def __init__(self, cfg_path):
        
        config = uu.get_config(cfg_path)
        self.cfg = config
        self.Root = self.cfg['Root']

        with open(os.path.join(self.Root, self.cfg['credentials']), 'r') as f:
            self.creds = f.read()
        