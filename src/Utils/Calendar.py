from datetime import datetime
import Utils.utils as uu
from telebot import types
import pandas as pd
import numpy as np
import os

class Schedule:
    def __init__(self, config_p):
        config = uu.get_config(config_p)
        self.available_times = np.array(config['available_times'])
        
        self.df_columns = ['date',
                        'time',  
                        'user',  
                        'event', 
                        'people',]
        self.available_times = np.array([
            '09:00',
            '10:00',
            '11:00',
            '12:00',
            '13:00',
            '14:00',
            '15:00',
            '16:00',
            '17:00',
            '18:00'
        ])
        self.schedule_csv = 'schedule.csv'
        self.schedule = pd.DataFrame(columns=self.df_columns)
        self.schedule.to_csv(self.schedule_csv, index=False)


        self.now  = datetime.now()
        self.y = self.now.year
        self.m  = self.now.month
        self.d   = self.now.day

    def read_schedule(self):
        self.schedule  = pd.read_csv(self.schedule_csv)

    def save_schedule(self):
        self.schedule.to_csv(self.schedule_csv, index=False)

    def drop_outdated(self):
        self.read_schedule()
        self.now = datetime.now()
        self.schedule = self.schedule[self.schedule['date'] >= self.now.strftime('%d.%m.%Y')]
        self.save_schedule()

    def add_schedule(self, date, time, user, event, people):
        row = pd.DataFrame({'date':date, 'time': time, 'user': user, 'event': event, 'people': people}, index=[0])
        self.read_schedule()
        self.schedule = pd.concat([self.schedule, row], ignore_index=True)
        self.save_schedule()

    
    def get_available_times(self, date):
        date = date.strftime('%d.%m.%Y')
        self.read_schedule()
        sch_day = self.schedule[self.schedule['date'] == date]
        sch_day_times = sch_day['time'].values
        
        av_times_mask = np.array([ False if elem in sch_day_times else True for elem in self.available_times])

        av_times = self.available_times[av_times_mask].tolist()
        self.save_schedule()

        return av_times


    def get_nowadays_month(self):
        now = datetime.now()
        return self.months[str(now.month)]
    
    def get_nowadays_year(self):
        now = datetime.now()
        return now.year
