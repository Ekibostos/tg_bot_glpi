import os
import re

import telebot;
from telebot import types;

import glpi_api


# Для авторизации бота в телеграм
bot = telebot.TeleBot('BOT_ID');

# Для авторизации в glpi
URL = 'GLPI_URL/apirest.php'
APPTOKEN = 'YOUR_APPTOKEN'
USERTOKEN = 'UOUR_USERTOKEN'


# Блокирует доступ всем пользователям кроме тех кто в списке users
# 
# Печатает в консоль user_id пользователей которые обращались к боту, но отсутствуют в списке
# Это сделано чтоб упростить поиск и добавление новых пользователей
def block_users(user_id):
    users = ['ID_YOUR_USERS']
    if user_id in users:
        return False
    else:
        print(user_id)
        return True


# Ищет через api glpi по имени компьютера или инвентарному номеру
def search_computer(q):
    try:
        with glpi_api.connect(URL, APPTOKEN, USERTOKEN) as glpi:
            row_json=str(glpi.get_all_items('Computer', range='0-10000'))
            row_json_m=row_json.split('[')
            for F in row_json_m:
                row_line = F.split('{')
                for T in row_line:
                    row_line1 = re.sub('[\]}{,:\']', '', T)
                    finish_line = row_line1.split()
                    #return(finish_line)
                    try:
                        if finish_line[9].lower() == q.lower():
                            return(finish_line[5])
                    except:
                        pass
                    try:
                        if finish_line[5].lower() == q.lower():
                            return(finish_line[9])
                    except:
                        pass
            return 0
    except:
        return 0


# Добавляет компьютер в glpi через api
def add_computer_glpi(num_c, name_c):
    if search_computer(num_c) == 0 and search_computer(name_c) == 0:
        with glpi_api.connect(URL, APPTOKEN, USERTOKEN) as glpi:
            glpi.add('Computer', {'name': name_c, 'otherserial': num_c})
            return('Компьютер добавлен, чтобы добавить ещё один введите /add')
    else:
        if search_computer(num_c) != 0:
            if search_computer(name_c) != 0:
                return('Ошибка добавления, компьютер с таким инвентарным номером и именем уже есть в системе, чтобы попробовать снова введите /add')
            else:
                return('Ошибка добавления, компьютер с таким инвентарным номером уже есть в системе, чтобы попробовать снова введите /add')
        else:
            return('Ошибка добавления, компьютер с таким именем уже есть в системе, чтобы попробовать снова введите /add')


@bot.message_handler(content_types=['text'])


def get_text_messages(message):
    if block_users(str(message.from_user.id)):
        bot.send_message(message.chat.id, 'Администратор не добавил вас в список пользователей этого бота')
        return
    if (message.text).lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет')
    elif message.text == "/help" or message.text == "/start":
        bot.send_message(message.chat.id, '''Отправь инвентарный номер или имя компьютера для поиска.
/add добаваить новый компьютер в GLPI''')
    elif message.text == "/add" or message.text == "/start":
        bot.send_message(message.chat.id, 'Введите инвентарный номер и имя компьютера через пробел')
        bot.register_next_step_handler(message, add_computer_glpi_i);
    elif ((message.text).lower()).find('add') > 0:
        vvod = (message.text).split()
        if vvod[0] == '/add':
            bot.send_message(message.chat.id, add_computer_glpi(vvod[1], vvod[2]))
        else:
            res = search_computer(str(message.text))
            if res == 0:
                bot.send_message(message.chat.id, 'Ничего не найдено')
            else:
                bot.send_message(message.chat.id, res)
    else:
        res = search_computer(str(message.text))
        if res == 0:
            bot.send_message(message.chat.id, 'Ничего не найдено')
        else:
            bot.send_message(message.chat.id, res)


def add_computer_glpi_i(message):
    vvod = (message.text).split()
    bot.send_message(message.chat.id, add_computer_glpi(vvod[0], vvod[1]))
    bot.register_next_step_handler(message, get_text_messages);


bot.polling(none_stop=True, interval=0)
