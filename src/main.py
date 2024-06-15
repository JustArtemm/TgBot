from Utils.config import BaseConfig
import argparse
import telebot
from telebot import types
from Print3D import Print3D
import os
import Utils.utils as uu
opj = os.path.join

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='Configs/base.json', help='config file path')
    args  = parser.parse_args()

    config  = BaseConfig(args.config)
    bot = telebot.TeleBot(config.creds)



    @bot.message_handler(commands=['start'])
    def start(message):

        # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # btn1 = types.KeyboardButton("Начать")
        # markup.add(btn1)
        bot.send_message(message.from_user.id, "👋 Привет! Я бот-помошник для личной 3d печати! Скинь мне файл в формате gcode и следуй инструкциям далее! Мой создатель: @just_artemm")

    @bot.message_handler(content_types=['document'])
    def get_file_messages(message):
        
        if message.document.file_name.endswith('.gcode'):

            bot.send_message(message.from_user.id, 'Вы отправили файл печати!')
            
            file_name = message.document.file_name
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_description= {
                'file_name': file_name,
                'file_type': file_name.split('.')[-1],
                'user_id': message.from_user.id,
                'user': message.from_user.username,
                'local_dir': opj(config.DataRoot, 'TelegramArchive', message.from_user.username),
            }

            if not os.path.isdir(file_description['local_dir']):
                os.makedirs(file_description['local_dir'])

            uu.dump_config(file_description, opj(file_description['local_dir'], file_description['file_name'].split('.')[0] + '.json'))
            

            with open(opj(file_description['local_dir'], file_description['file_name']), 'wb') as f:
                f.write(downloaded_file)

            bot.send_message(message.from_user.id, 'Информация о файле успешно сохранена, проверка параметров печати')
            
            printer = Print3D(file_description)
        
        elif message.document.file_name.endswith('.stl'):
            bot.send_message(message.from_user.id, 'На данный момент поддерживается лишь формат файлов gcode')
            pass
        else:
            bot.send_message(message.from_user.id, 'На данный момент поддерживается лишь формат файлов gcode')
    
    bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть