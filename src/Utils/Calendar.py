from datetime import datetime
from datetime import timedelta
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
        self.events  = config['events']
        self.schedule_csv = 'schedule.csv'
        self.schedule = pd.DataFrame(columns=self.df_columns)
        self.schedule.to_csv(self.schedule_csv, index=False)

        self.weekdays = {
            0: 'monday',
            1: 'tuesday',
            2: 'wednesday',
            3: 'thursday',
            4: 'frday',
            5: 'saturday',
            6: 'sunday',

        }


        self.now  = datetime.now()
        self.y = self.now.year
        self.m = self.now.month
        self.d = self.now.day

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

    def sum_times(self, times:list):
        mysum = timedelta()
        for elem in times:
            h, m = elem.split(':')
            d = timedelta(hours=int(h), minutes=int(m))
            mysum += d
        return str(mysum).rsplit(':',1)[0]
    
    def get_remaining_times(self, t_from, t_to, date):
        weekday = self.weekdays[date.weekday()]
        events = self.events[weekday]
        banned_times = [[events[elem]['start'], self.sum_times([events[elem]['start'], events[elem]['lasts']])] for elem in events]
        times_to_stay = self.available_times

        for i in range(len(self.available_times)):
            for j in range(len(banned_times)):
                c = 0
                t_from  = banned_times[j][0]
                t_to   = banned_times[j][1]

                if t_from <= self.available_times[i] <= t_to:
                    #banned_times.append([self.available_times[i], self.available_times[i]])
                    times_to_stay.remove(self.available_times[i])
        return times_to_stay
    
    # def make_events4today(self):


    
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
