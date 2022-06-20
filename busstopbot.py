import telebot
from telebot import types
import sqlite3
from busstops import *
# Создаем экземпляр бота
bot = telebot.TeleBot('5379865435:AAEnH71gB6uAEOA0ZThNUz7TwxcPgvEcX8o')
conn = None

conn = sqlite3.connect('busbotdatabase.db', check_same_thread=False)
cursor = conn.cursor()

def db_table_val(user_name: str, group_name: str, bus_stop_name: str):
	cursor.execute('INSERT INTO busbot (user_name, group_name, bus_stop_name) VALUES (?, ?, ?)', (user_name, group_name, bus_stop_name))
	conn.commit()

def db_table_group(user_name: str):
    sql = 'SELECT DISTINCT group_name FROM busbot WHERE user_name=:user_name'
    return cursor.execute(sql,{'user_name':user_name})

def db_table_stops(user_name: str, group_name: str):
    sql = 'SELECT bus_stop_name FROM busbot WHERE user_name=:user_name AND group_name=:group_name'  
    return cursor.execute(sql,{'user_name':user_name, 'group_name':group_name})

def db_delete_group(user_name: str, group_name: str):
    sql = 'DELETE FROM busbot WHERE user_name=:user_name AND group_name=:group_name'  
    return cursor.execute(sql,{'user_name':user_name, 'group_name':group_name})

def default_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton(text='Add')
    btn2 = telebot.types.KeyboardButton(text='Delete')
    btn3 = telebot.types.KeyboardButton(text='Show')
    markup.add(btn1,btn2,btn3)
    return markup

# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(message):
    markup = default_markup()
    bot.send_message(message.from_user.id, 'Йо, сюда можно скидывать ссылки на остановки из приложения Московский транспорт.\n\nНо, чтобы ты мог ими оперативно пользоваться можешь добавить группы остановок.',reply_markup=markup)


# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def reply(message):
    txt = message.text
    if txt == 'Add':
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(telebot.types.KeyboardButton(text='Back'))
        msg = bot.send_message(message.from_user.id, 'Отправьте ссылку из Московского транспорта и группу, куда хотели бы включить остановку',reply_markup=markup)
        bot.register_next_step_handler(msg, askLink)
    if txt == 'Show':
        groupList = db_table_group(message.from_user.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row_width = 2
        for group in groupList:
            group[0].title()
            keyboard.add(telebot.types.InlineKeyboardButton(group[0].title(), callback_data=group[0]))
        bot.send_message(message.from_user.id,'Выберите группу',reply_markup = keyboard)
    if txt == 'Delete':
        groupList = db_table_group(message.from_user.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row_width = 2
        for group in groupList:
            group[0].title()
            keyboard.add(telebot.types.InlineKeyboardButton(group[0].title(), callback_data='~`0'+group[0]))
        bot.send_message(message.from_user.id,'Выберите группу для удаления',reply_markup = keyboard)

@bot.callback_query_handler(func=lambda call: call.data[0:2] == '~`')
def deleteGroup(call):
    db_delete_group(call.from_user.id,call.data[3:].lower())
    conn.commit()
    bot.send_message(call.from_user.id,'Удалили')    

@bot.callback_query_handler(func=lambda call: call.data[0] != '~')
def query_handler(call):
    stopList = db_table_stops(call.from_user.id,call.data)
    stopList = [x[0] for x in stopList]
    imageGen(stopList)
    photo = open('out2.png','rb')
    bot.send_photo(call.from_user.id,photo)

def askLink(message):
    txt = message.text
    if txt[0:28] == 'https://moscowtransport.app/':
        msg = bot.send_message(message.from_user.id, 'Похожа на нужную, а теперь группу')
        bot.register_next_step_handler(msg, askGroup,txt)
    elif txt == 'Back':
        bot.send_message(message.from_user.id,'Вернулись к началу',reply_markup=default_markup())
        return
    else:
        msg = bot.send_message(message.from_user.id, 'Не очень похоже на нужную ссылку, может еще раз?')
        bot.register_next_step_handler(msg, askLink)
   

def askGroup(message,link):
    txt = message.text  
    if txt == 'Back':
        bot.send_message(message.from_user.id,'Вернулись к началу',reply_markup=default_markup())
        return
    db_table_val(message.from_user.id,txt.lower(),link)
    bot.send_message(message.chat.id, 'Добавили',reply_markup=default_markup())





# Запускаем бота
bot.polling(none_stop=True, interval=0)