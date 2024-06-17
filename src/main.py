from Utils.config import BaseConfig
import argparse
import telebot
from telebot import types
from datetime import datetime
from Utils.Calendar import Schedule

from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
# from telebot

from telebot.types import ReplyKeyboardRemove, CallbackQuery


def get_main_screen():
    main_screen = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Запись')
    btn2 = types.KeyboardButton('Рассылка')
    main_screen.add(btn1, btn2)
    return main_screen

def gen_times_markup(date, times):
    markup = types.InlineKeyboardMarkup(row_width = 3)
    for i in range(len(times)):
        markup.add(types.InlineKeyboardButton(times[i], callback_data=f'datetime+{date}+{times[i]}'))
    return markup

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='Configs/base.json', help='config file path')
    args  = parser.parse_args()

    

    config  = BaseConfig(args.config)
    bot = telebot.TeleBot(config.creds)
    calendar = Calendar(language=RUSSIAN_LANGUAGE)
    schedule = Schedule(config.schedule_cfg)
    
    # Creates a unique calendar
    calendar = Calendar(language=RUSSIAN_LANGUAGE)
    calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")

    @bot.message_handler(commands=['start'])
    def start(message):

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Начать")
        markup.add(btn1)
        bot.send_message(message.from_user.id, "👋 Привет! Я бот-помошник! Для записи нажмите кнопку Начать! Мой создатель: @just_artemm", reply_markup=markup)



    @bot.message_handler(content_types=['text'])
    def check_other_messages(message):
        """
        Catches a message with the command "start" and sends the calendar

        :param message:
        :return:
        """

        if message.text == 'Начать':
            
            bot.send_message(message.from_user.id, 'Здесь должна быть надпись', reply_markup=get_main_screen()) #ответ бота
        if message.text == 'Запись':

            now = datetime.now()  # Get the current date
            bot.send_message(
                message.chat.id,
                "Выберите дату",
                reply_markup=calendar.create_calendar(
                    name=calendar_1_callback.prefix,
                    year=now.year,
                    month=now.month,  # Specify the NAME of your calendar
                ),
            )

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith('datetime')
    )
    def callback_time_inline(call: CallbackQuery):

        name, date, time = call.data.split('+')
        schedule.add_schedule(date=date, time=time, user = call.from_user.username, people=None, event=None)

        # link_markup = types.InlineKeyboardMarkup(row_width=3)
        # print(call)
        bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id-1)
        
        bot.send_message(
                chat_id=call.from_user.id,
                text=f"Вы записаны {date} на {time}",
                reply_markup=get_main_screen(),
            )
        
        schedule.drop_outdated()
        

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith(calendar_1_callback.prefix)
    )
    def callback_date_inline(call: CallbackQuery):
        """
        Обработка inline callback запросов
        :param call:
        :return:
        """
        # print(call.data)
        # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
        name, action, year, month, day = call.data.split(calendar_1_callback.sep)
        # Processing the calendar. Get either the date or None if the buttons are of a different type
        date = calendar.calendar_query_handler(
            bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
        )
        # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
        if action == "DAY":
            bot.send_message(
                chat_id=call.from_user.id,
                text=f"Выбранная дата: {date.strftime('%d.%m.%Y')}",
                reply_markup=ReplyKeyboardRemove(),
            )
            times_list = schedule.get_available_times(date=date)
            print(times_list)
            
            
            bot.send_message(
                chat_id=call.from_user.id,
                text="Выберите доступное время",
                reply_markup=gen_times_markup(date.strftime('%d.%m.%Y'),times_list),
            )
            
            # print(f"{calendar_1_callback}: Day: {date.strftime('%d.%m.%Y')}")
        elif action == "CANCEL":
            bot.send_message(
                chat_id=call.from_user.id,
                text="Отмена",
                reply_markup=ReplyKeyboardRemove(),
            )
            print(f"{calendar_1_callback}: Cancellation")


    bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть