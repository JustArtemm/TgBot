from datetime import datetime
import Utils.utils as uu
from telebot import types

class Calendar:
    def __init__(self):
        self.months = {
            '01' : "Январь",
            '02' : "Февраль",
            '03' : "Март",
            '04' : "Апрель",
            '05' : "Май",
            '06' : "Июнь",
            '07' : "Июль",
            '08' : "Август",
            '09' : "Сентябрь",
            '10' : "Октябрь",
            '11' : "Ноябрь",
            '12' : "Декабрь"
        }
        now  = datetime.now()
        self.y = now.year
        self.m  = now.month
        self.d   = now.day

    def get_nowadays_month(self):
        now = datetime.now()
        return self.months[str(now.month)]
    
    def get_nowadays_year(self):
        now = datetime.now()
        return now.year
