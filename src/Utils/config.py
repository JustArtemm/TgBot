import os, sys, json
import Utils.utils as uu

class BaseConfig():
    """
    Base configuration class.
    """
    def __init__(self, cfg_path):
        self.cfg_path= cfg_path
        config = uu.get_config(cfg_path)
        self.cfg = config
        self.Root = self.cfg['Root']
        self.schedule_cfg = self.cfg['schedule_cfg']
        self.subs_cfg  = self.cfg['subscription_cfg']
        self.admin_users = self.cfg['admin_users']
        self.secret_admin_code = self.cfg['secret_admin_code']
        with open(os.path.join(self.Root, self.cfg['bot_credentials']), 'r') as f:
            self.creds = f.read()
    def dump_data(self):
        uu.dump_config(self.cfg, self.cfg_path)
        