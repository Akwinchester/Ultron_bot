import telebot
from config import BOT_TOKEN, MESSAGE_TEXT, BUTTON_TEXT
from models.user import create_user
from models.activity import formation_list_activity, add_activity, get_name_activity, delete_activity
from keyboards import make_keyboard_start, make_keyboard_main_menu,\
    make_keyboard_list_activity, make_keyboard_skip_amount,\
    make_keyboard_skip_description, make_keyboard_setting_activity, make_keyboard_setting_push
from models.entry import add_row
from data_structares import Row, RowFactory

from datetime import date
from keyboa import Keyboa
import re

message_id_for_edit = {}
user_row = {}


bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')


#Приветственное сообщение
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!!!\n'+MESSAGE_TEXT['start'],
                     reply_markup=make_keyboard_start())

    create_user(message.from_user.first_name, message.chat.id)


#Открытие главного меню
@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['start'])
def go_main_menu(message):
    bot.send_message(message.chat.id, MESSAGE_TEXT['main_menu'], reply_markup=make_keyboard_main_menu())


#Возвращение в главное меню через кнопку отмены
@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['cancel'])
def return_main_menu(message):
    bot.send_message(message.chat.id, MESSAGE_TEXT['main_menu'], reply_markup=make_keyboard_main_menu())


#Обработка нажатия кнопки "Добавить запись"
@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['add_row'])
def add_row_button(message):
    bot.delete_message(message.chat.id, message.id)
    keyboard = make_keyboard_list_activity(message.chat.id)
    bot.send_message(message.chat.id, 'Выбери или создай активность', reply_markup=keyboard())


#Обработка нажатия кнопки добавлене активности "добавить запись"->"+"
@bot.callback_query_handler(func=lambda call: call.data == 'activity=add_activity')
def callback_inline(call):
    answer = bot.send_message(call.message.chat.id, 'отправь название новой активности следующим сообщением')
    message_id_for_edit['list_activity'] = call.message.id
    message_id_for_edit['name_activity'] = answer.message_id
    bot.register_next_step_handler(call.message, get_name_new_activity)


#Получение имени новой активности от пользователя из сообщения
def get_name_new_activity(message):
    chat_id = message.chat.id
    add_activity(chat_id, name_activity=message.text)

    keyboard = make_keyboard_list_activity(chat_id)
    bot.delete_message(chat_id, message.id)
    bot.delete_message(chat_id, message_id_for_edit['name_activity'])
    bot.edit_message_text(text='Выбери или создай активность', message_id=message_id_for_edit['list_activity'],
                          chat_id=message.chat.id,
                          reply_markup=keyboard())


#Обработка нажатия на кнопку выбора активности "Добавить запись"->"имя_активности"
@bot.callback_query_handler(func=lambda call: re.match(r'activity=[0-9]+',call.data))
def callback_inline(call):
    chat_id = call.message.chat.id
    activity_id = call.data.split('=')[1]
    message_id_for_edit['list_activity'] = call.message.id
    keyboard = make_keyboard_setting_activity(activity_id)
    bot.edit_message_text(f'Выбранная активность: {get_name_activity(activity_id)}', chat_id, call.message.id, reply_markup=keyboard())


#Удаление активности "Добавить запись"->"имя_активности"->"Удалить активность"
@bot.callback_query_handler(func=lambda call: re.match(r'activity_[0-9]+=delete',call.data))
def callback_inline(call):
    activity_id = call.data.split('=')[0].split('_')[1]
    delete_activity(activity_id)

    keyboard = make_keyboard_list_activity(call.message.chat.id)
    bot.edit_message_text('Выбери или создай активность',call.message.chat.id, call.message.id, reply_markup=keyboard())
    # bot.send_message(message.chat.id, 'Выбери или создай активность', reply_markup=keyboard())


#Обраотка нажатия на кнопку "уведомления" из (удалить активность, уведомления, продолжить)
@bot.callback_query_handler(func=lambda call: re.match(r'activity_[0-9]+=push',call.data))
def callback_inline(call):
    keyboard = make_keyboard_setting_push()
    activiy_name = get_name_activity(call.data.split('=')[0].split('_')[1])
    bot.edit_message_text(f'Настройка текста уведомления и получателей уведомления для активности: <b>{activiy_name}</b>',
                          call.message.chat.id, call.message.id, reply_markup=keyboard())


#Обработка "уведомления"->"список активностей" или "имя_активности"->"список активностей"
@bot.callback_query_handler(func=lambda call: re.match(r'push=save|activity_[0-9]+=list_activity',call.data))
def list_activity(call):
    keyboard = make_keyboard_list_activity(call.message.chat.id)
    bot.edit_message_text('Выбери или создай активность', call.message.chat.id, call.message.id, reply_markup=keyboard())


#Обработка "уведомления"->"текст уведомления"
@bot.callback_query_handler(func=lambda call: re.match(r'push=text',call.data))
def list_activity(call):
    answer = bot.send_message(call.message.chat.id, MESSAGE_TEXT['example_push'])
    message_id_for_edit['push_setting_text'] = answer.id
    bot.register_next_step_handler(call.message, get_text_push)


#Забираю текст уведомления от пользователя из сообщения
def get_text_push(message):
    print(message.text) #здесь должна быть обработка текста сообщения
    bot.delete_message(message.chat.id, message_id_for_edit['push_setting_text'])
    bot.delete_message(message.chat.id, message.id)


#Обработка "уведомления"->"получатели"
@bot.callback_query_handler(func=lambda call: re.match(r'push=addresses',call.data))
def list_activity(call):
    answer = bot.send_message(call.message.chat.id, MESSAGE_TEXT['example_push'])
    message_id_for_edit['push_setting_text'] = answer.id
    bot.register_next_step_handler(call.message, get_text_push)



#Обработка выбора активности
@bot.callback_query_handler(func=lambda call: re.match(r'activity_[0-9]+=continue',call.data))
def callback_inline(call):
    chat_id = call.message.chat.id
    activity_id = call.data.split('=')[0].split('_')[1]
    bot.delete_message(chat_id, message_id_for_edit['list_activity'])
    user_row[chat_id] = RowFactory()
    user_row[chat_id].set_activity_id(activity_id)
    keyboard = make_keyboard_skip_amount()
    bot.send_message(chat_id, 'Можешь указать количественную характеристику', reply_markup=keyboard())


#Получаем количественную характеристику
@bot.callback_query_handler(func=lambda call: re.match(r'amount=continue',call.data))
def callback_inline(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    answer = bot.send_message(call.message.chat.id, 'Отправь количество следующим сообщением')
    message_id_for_edit['amount_continue'] = answer.id
    bot.register_next_step_handler(call.message, get_amount)


#Получение количественной характеристики от пользователя из сообщения
def get_amount(message):
    user_row[message.chat.id].set_amount(int(message.text))
    bot.delete_message(chat_id=message.chat.id, message_id=message_id_for_edit['amount_continue'])
    bot.delete_message(message.chat.id, message.id)

    keyboard = make_keyboard_skip_description()
    answer = bot.send_message(message.chat.id, 'Можешь добавить описание', reply_markup=keyboard())
    message_id_for_edit['description_cskip'] = answer.id


#Пропускаем ввод количественной характеристики
@bot.callback_query_handler(func=lambda call: re.match(r'amount=skip',call.data))
def callback_inline(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    user_row[message.chat.id].set_amount(0)
    keyboard = make_keyboard_skip_description()
    bot.send_message(call.message.chat.id, 'Можешь добавить описание', reply_markup=keyboard())



#Получение описания
@bot.callback_query_handler(func=lambda call: re.match(r'description=continue',call.data))
def callback_inline(call):
    answer = bot.send_message(call.message.chat.id, 'Отправь описание следующим сообщением')
    message_id_for_edit['description_cskip'] = answer.id

    bot.delete_message(call.message.chat.id, call.message.id)
    bot.register_next_step_handler(call.message, get_description)


#Получение описания от пользователя из сообщения
def get_description(message):
    user_row[message.chat.id].set_description(message.text)
    user_row[message.chat.id].set_date_added(date.today())
    bot.delete_message(message.chat.id, message.id)
    bot.delete_message(message.chat.id, message_id_for_edit['description_cskip'])
    finish_step_add_row(user_row[message.chat.id])


#Обрабатываем пропускание описания
@bot.callback_query_handler(func=lambda call: re.match(r'description=skip',call.data))
def callback_inline(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    user_row[call.message.chat.id].set_description('-')
    user_row[call.message.chat.id].set_date_added(date.today())
    finish_step_add_row(user_row[call.message.chat.id])


#Этап создания объекта Row и записи данных в БД
def finish_step_add_row(row_maker):
    row = row_maker.create_row()
    add_row(row)

if __name__ == '__main__':
    bot.infinity_polling(none_stop=True)