import os
import sys
import argparse
import Utils.utils as uu


class Subscription:
    def __init__(self, config_p):
        self.config_p = config_p
        self.config = uu.get_config(config_p)
        self.user_list = self.config["users"]
        self.messages = self.config["messages"]

    def get_message(self, intterval):
        message = self.messages[intterval]['text']
        return message
    
    def dump_data(self):
        self.config["users"] = self.user_list
        # self.config["messages"]  = self.messages
        uu.dump_config(self.config, self.config_p)
    def remove_user(self, user):
        self.user_list.remove(user)
        self.dump_data()
    def add_user(self, user):
        self.user_list.append(user)
        self.dump_data()


