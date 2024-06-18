import os
import sys
import argparse
import Utils.utils as uu
import schedule as sc


class Subscription:
    def __init__(self, config_p):
        self.config_p = config_p
        self.config = uu.get_config(config_p)
        self.user_list = self.config["users"]
        self.messages = self.config["messages"]
        
    def get_empty_message(self):
        message = {
            "text"  : '',
            "period": '1h'
        }
        return message

    # def every_period(self, period):
    #     sc.every(5).seconds.do(every5s)
    #     return sc
    def create_sub(self, message = 'None', period = '5s', replace = False):
        empty_message  = self.get_empty_message()
        empty_message["text"]= message.text
        empty_message["period"]= period
        self.messages.append(empty_message)
        if replace:
            self.messages = [empty_message]

    def format_time(self, str_time, function):
        """
        str_time : '3h' means 3 hours
        """
        amount, units = str_time.split('')
        if 's' == units:
            sc.every(amount).seconds.do(function)
        if 'm'  == units:
            sc.every(amount).minutes.do(function)
        if 'h'  == units:
            sc.every(amount).hours.do(function)
        if 'd'  == units:
            sc.every(amount).days.do(function)
        if 'w'  == units:
            sc.every(amount).weeks.do(function)
        if 'y'  == units:
            sc.every(amount).years.do(function)
        return sc




    def get_message(self, intterval):
        message = [elem['text'] for elem in self.messages if intterval  == elem['period']][0]
        # message = self.messages[intterval]['text']
        return message
    
    def dump_data(self):
        self.config["users"] = self.user_list
        self.config["messages"]  = self.messages
        uu.dump_config(self.config, self.config_p)
    def remove_user(self, user):
        self.user_list.remove(user)
        self.dump_data()
    def add_user(self, user):
        self.user_list.append(user)
        self.dump_data()



