from Utils.config import BaseConfig
import argparse
import telebot
import schedule as sc
import threading
from telebot import types
from datetime import datetime
from Utils.Calendar import Schedule
from Utils.Subscription import Subscription
import time
import numpy as np


from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
# from telebot

from telebot.types import ReplyKeyboardRemove, CallbackQuery
messages_to_delete = []

def get_users_main_screen():
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

def every5s():
    global args
    config  = BaseConfig(args.config)
    # print('im_in_every8s')
    subs = Subscription(config.subs_cfg)
    
    users = []
    markup_subscription = types.InlineKeyboardMarkup(row_width = 3)
    markup_subscription.add(types.InlineKeyboardButton("Отказаться от рассылки", callback_data=f'subscription+remove'))
    for i in range(len(subs.user_list)):
        try:
            msg = subs.get_message('5s')
            bot.send_message(
                chat_id=subs.user_list[i],
                text=msg,
                reply_markup=markup_subscription,
            )
            users.append(subs.user_list[i])
        except:
            # users.append(subs.user_list[i])
            pass
        time.sleep(1)
    subs.user_list = np.unique(users).tolist()
    subs.dump_data()

def get_main_screen(user):
    global args
    config  = BaseConfig(args.config)

    if user in config.admin_users:
        return get_admin_main_screen()
    else:
        return get_users_main_screen()

def get_admin_main_screen():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Посмотреть расписание')
    btn2 = types.KeyboardButton('Создать сообщение для рассылки')
    btn3 = types.KeyboardButton('Добавить администратора')
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    return markup
            

def subscription():
    # print('im_in_subscription')
    # subs = Subscription(config.subs_cfg)
    sc.every(5).seconds.do(every5s)
    while True:
        sc.run_pending()
        time.sleep(1)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='Configs/base.json', help='config file path')
    args  = parser.parse_args()

    

    config  = BaseConfig(args.config)
    bot = telebot.TeleBot(config.creds)
    schedule = Schedule(config.schedule_cfg)
    
    # Creates a unique calendar
    calendar = Calendar(language=RUSSIAN_LANGUAGE)
    calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")
    calendar_admin_callback = CallbackData("calendar_admin", "action", "year", "month", "day")

    thread = threading.Thread(target=subscription)
    
    @bot.message_handler(func= lambda message: message.from_user.id in BaseConfig(args.config).admin_users ,commands=['start'])
    def start_admin(message):
        bot.send_message(message.from_user.id, 
                    "👋 Добро пожаловать в доступ администратора! Мой создатель: @just_artemm, пишите по вопросам работы бота", 
                    reply_markup=get_main_screen(message.from_user.id))

    @bot.message_handler(func= lambda message:not message.from_user.id in BaseConfig(args.config).admin_users ,commands=['start'])
    def start_users(message):

        bot.send_message(message.from_user.id, 
                         "👋 Привет! Я бот-помошник! Для записи нажмите кнопку Начать!", 
                         reply_markup=get_main_screen(message.from_user.id))
    
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith(calendar_admin_callback.prefix)
    )
    def admin_calendar_handler(call: CallbackQuery):
        
        name, action, year, month, day = call.data.split(calendar_admin_callback.sep)
        # Processing the calendar. Get either the date or None if the buttons are of a different type
        date = calendar.calendar_query_handler(
            bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
        )
        # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
        if action == "DAY":
            bot.send_message(
                chat_id=call.from_user.id,
                text=f"Выбранная дата: {date.strftime('%d.%m.%Y')}",
                reply_markup=get_main_screen(call.from_user.id),
            )

            opt_msg = schedule.view_schedule(date=date)
            
            # times_list = schedule.get_available_times(date=date)
            # print(times_list)
            
            
            bot.send_message(
                chat_id=call.from_user.id,
                text=opt_msg,
                reply_markup=get_main_screen(call.from_user.id),
            )
            
            # print(f"{calendar_1_callback}: Day: {date.strftime('%d.%m.%Y')}")
        elif action == "CANCEL":
            bot.send_message(
                chat_id=call.from_user.id,
                text="Отмена",
                reply_markup=ReplyKeyboardRemove(),
            )
            print(f"{calendar_admin_callback}: Cancellation")



    @bot.message_handler(func= lambda message: message.from_user.id in BaseConfig(args.config).admin_users ,content_types=['text'])
    def admin_messages_handler(message):
        if message.text  ==  'Посмотреть расписание':

            now = datetime.now()  # Get the current date
            bot.send_message(
                message.from_user.id,
                "Выберите дату",
                reply_markup=calendar.create_calendar(
                    name=calendar_admin_callback.prefix,
                    year=now.year,
                    month=now.month,  # Specify the NAME of your calendar
                ),
            )
        elif message.text ==  'Создать сообщение для рассылки':
            global new_sub_message_creation
            new_sub_message_creation = bot.send_message(
                message.chat.id,
                "Введите сообщение",
                reply_markup=ReplyKeyboardRemove()  
                )
            # print(new_sub_message_creation.id)
        elif message.text ==   'Добавить администратора':
            global new_admin_input_msg
            new_admin_input_msg = bot.send_message(message.from_user.id, "Попросите желаемого администратора отправить слледующее сообщение боту")
            new_admin_input_msg = bot.send_message(message.from_user.id, 
                                                   f'/op {BaseConfig(args.config).secret_admin_code}', 
                                                   reply_markup=get_main_screen(message.from_user.id))
            
            # config = BaseConfig(args.config)



        else:
            
            try:
                if message.id - new_sub_message_creation.id == 1:
                    subs = Subscription(BaseConfig(args.config).subs_cfg)
                    subs.create_sub(message = message, replace= True)
                    subs.dump_data()
                    bot.send_message(
                        message.chat.id,
                        "Добавлено новое сообщение с рассылкой",
                        reply_markup=get_main_screen(message.from_user.id)  
                        )
                # elif new_admin_input_msg.id - message.id == 1:
                #     config = BaseConfig(args.config)
                #     config.admin_users_toverify.append(message.text.split('@')[::-1][0])
                #     bot.send_message(
                #         message.chat.id,
                #         f"Администратор {message.text.split('@')[::-1][0]} добавлен",
                #         reply_markup=get_main_screen(message.from_user.id)  
                #         )
                #     bot.send_message(
                #         297516646,
                #         f"!!Администратор добавлен!! {message.text.split('@')[::-1][0]}",
                #         reply_markup=get_main_screen(message.from_user.id)  
                #         )
            except:
                pass
    
    @bot.message_handler(func= lambda message: not  message.from_user.id in BaseConfig(args.config).admin_users ,commands=['op'])
    def add_new_admin(message):
        # print(message.from_user.id  in BaseConfig(args.config).admin_users)
        if message.text.rsplit(' ', 1)[1] == BaseConfig(args.config).secret_admin_code:
            if not message.from_user.id  in BaseConfig(args.config).admin_users:
                config = BaseConfig(args.config)
                config.admin_users.append(message.from_user.id)
                config.dump_data()
                bot.send_message(
                    message.chat.id,
                    f"Вы теперь администратор",
                    reply_markup=get_main_screen(message.from_user.id)  
                    )
            else:
                bot.send_message(
                    message.chat.id,
                    f"Вы уже являетесь администратором",
                    reply_markup=get_main_screen(message.from_user.id)  
                    )
        else:
            bot.send_message(
                message.chat.id,
                f"Неизвестная команда",
                reply_markup=get_main_screen(message.from_user.id)  
                )

    

    @bot.message_handler(func= lambda message: not  message.from_user.id in BaseConfig(args.config).admin_users ,content_types=['text'])
    def check_other_messages(message):
        """
        Catches a message with the command "start" and sends the calendar

        :param message:
        :return:
        """

        if message.text == 'Начать':
            
            bot.send_message(message.from_user.id, 'Здесь должна быть надпись', reply_markup=get_main_screen(message.from_user.id)) #ответ бота
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
        if message.text ==  'Рассылка':
            markup_subscription = types.InlineKeyboardMarkup(row_width = 3)
            markup_subscription.add(types.InlineKeyboardButton("Подписаться на рассылку", callback_data=f'subscription+add'))

            bot.send_message(message.chat.id, 
                             'Вы можете подписаться на рассылку нажав на кнопку ниже', 
                             reply_markup=markup_subscription)

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith('subscription')
    )
    def callback_subscription(call: CallbackQuery):
        # global config
        name, status = call.data.split('+')
        if status == 'remove':
            subs = Subscription(BaseConfig(args.config).subs_cfg)
            subs.remove_user(call.from_user.id)
            bot.send_message(call.from_user.id, 
                             'Вы отписались от рассылки, вы всегда можете подписаться на нее снова в соответствующем разделе', 
                             reply_markup=get_main_screen(call.from_user.id))
        else:
            subs = Subscription(BaseConfig(args.config).subs_cfg)
            subs.add_user(call.from_user.id)
            bot.send_message(call.from_user.id, 
                             'Вы подписались на рассылку, вы всегда можете отписаться от рассылки', 
                             reply_markup=get_main_screen(call.from_user.id))
        


    @bot.callback_query_handler(
        func=lambda call: call.data.startswith('datetime')
    )
    def callback_time_inline(call: CallbackQuery):

        # bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

        name, date, time = call.data.split('+')
        
        schedule.add_schedule(date=date, time=time, user = call.from_user.username, people=None, event=None)

        # link_markup = types.InlineKeyboardMarkup(row_width=3)
        # print(call)

        bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        # bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id-1)

        if date < datetime.now().strftime('%d.%m.%Y'):
            bot.send_message(
                chat_id=call.from_user.id,
                text=f"Выбрана прошедшая дата {date}, повторите запись",
                reply_markup=get_main_screen(call.from_user.id),
            )
        else:
            bot.send_message(
                    chat_id=call.from_user.id,
                    text=f"Вы записаны {date} на {time}",
                    reply_markup=get_main_screen(call.from_user.id),
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
                reply_markup=get_main_screen(call.from_user.id),
            )
            
            times_list = schedule.get_available_times(date=date)
            # print(times_list)
            
            
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

    thread.start()
    bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть