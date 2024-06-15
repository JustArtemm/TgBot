from Utils.config import BaseConfig
import argparse
import telebot
from telebot import types


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='Configs/base.json', help='config file path')
    args  = parser.parse_args()

    config  = BaseConfig(args.config)
    bot = telebot.TeleBot(config.creds)



    @bot.message_handler(commands=['start'])
    def start(message):

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("👋 Поздороваться")
        markup.add(btn1)
        bot.send_message(message.from_user.id, "👋 Привет! Я бот-помошник! Мой создатель: @just_artemm", reply_markup=markup)

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):

        if message.text == 'Сообщение1':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
            btn1 = types.KeyboardButton('Сообщение1.1')
            btn2 = types.KeyboardButton('Сообщение1.2')
            btn3 = types.KeyboardButton('Собщение1.3')
            markup.add(btn1, btn2, btn3)
            bot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос', reply_markup=markup) #ответ бота


        elif message.text == 'Сообщение1.1':
            bot.send_message(message.from_user.id, 'Ответ1.1', parse_mode='Markdown')

        elif message.text == 'Сообщение1.2':
            bot.send_message(message.from_user.id, 'Ответ1.2', parse_mode='Markdown')

        elif message.text == 'Собщение1.3':
            bot.send_message(message.from_user.id, 'Ответ1.3', parse_mode='Markdown')


    bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть