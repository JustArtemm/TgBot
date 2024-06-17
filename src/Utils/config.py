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
        self.schedule_cfg = self.cfg['schedule_cfg']

        with open(os.path.join(self.Root, self.cfg['bot_credentials']), 'r') as f:
            self.creds = f.read()
        