import telebot
from config import BOT_TOKEN, MESSAGE_TEXT, BUTTON_TEXT
from formation_text_message import select_activity, setting_notification, tg_entry_text
from models.user import create_user, get_user_id, add_friend
from models.activity import formation_list_activity, add_activity, get_name_activity, delete_activity,\
    update_notification_text, add_address, formation_list_adresses, formation_message_list_adresses, formation_list_chat_id, get_notification_text

from keyboards import make_keyboard_start, make_keyboard_main_menu,\
    make_keyboard_list_activity, make_keyboard_skip_amount,\
    make_keyboard_skip_description, make_keyboard_setting_activity, make_keyboard_setting_push, make_keyboard_list_friend

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

    create_user(message.from_user.first_name, message.chat.id, message.from_user.username)


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
@bot.callback_query_handler(func=lambda call: re.match(r'activity=[0-9]+\b',call.data))
def callback_inline(call):
    chat_id = call.message.chat.id
    activity_id = call.data.split('=')[1]
    message_id_for_edit['list_activity'] = call.message.id
    keyboard = make_keyboard_setting_activity(activity_id)
    bot.edit_message_text(select_activity(activity_id), chat_id, call.message.id, reply_markup=keyboard())


#Удаление активности "Добавить запись"->"имя_активности"->"Удалить активность"
@bot.callback_query_handler(func=lambda call: re.match(r'activity_[0-9]+=delete',call.data))
def callback_inline(call):
    activity_id = call.data.split('=')[0].split('_')[1]
    delete_activity(activity_id)

    keyboard = make_keyboard_list_activity(call.message.chat.id)
    bot.edit_message_text('Выбери или создай активность',call.message.chat.id, call.message.id, reply_markup=keyboard())



#Обраотка нажатия на кнопку "уведомления" из (удалить активность, уведомления, продолжить)
@bot.callback_query_handler(func=lambda call: re.match(r'activity_[0-9]+=push',call.data))
def callback_inline(call):
    activity_name = get_name_activity(call.data.split('=')[0].split('_')[1])
    activity_id = call.data.split('=')[0].split('_')[1]
    keyboard = make_keyboard_setting_push(activity_id)
    message_id_for_edit['activity_settings_menu'] = call.message.id
    # TODO: сделать формирование текстового сообщения
    bot.edit_message_text(setting_notification(activity_id),
                          call.message.chat.id, call.message.id, reply_markup=keyboard())


#Обработка "уведомления"->"список активностей" или "имя_активности"->"список активностей"
@bot.callback_query_handler(func=lambda call: re.match(r'[0-9]+_push=save|activity_[0-9]+=list_activity|activity=[0-9]+_friend=list_activity',call.data))
def list_activity(call):
    keyboard = make_keyboard_list_activity(call.message.chat.id)
    bot.edit_message_text('Выбери или создай активность', call.message.chat.id, call.message.id, reply_markup=keyboard())


#Обработка "уведомления"->"текст уведомления"
@bot.callback_query_handler(func=lambda call: re.match(r'[0-9]+_push=text',call.data))
def list_activity(call):
    answer = bot.send_message(call.message.chat.id, MESSAGE_TEXT['example_push'])
    message_id_for_edit['push_setting_text'] = answer.id
    activity_id = call.data.split('=')[0].split('_')[0]
    bot.register_next_step_handler(call.message, get_text_push, activity_id)


#Забираю текст уведомления от пользователя из сообщения
def get_text_push(message, activity_id):
    update_notification_text(activity_id=activity_id, notification_text=message.text)
    keyboard = make_keyboard_setting_push(activity_id)
    bot.edit_message_text(f'Настройка текста уведомления и получателей уведомления для активности: <b>{get_name_activity(activity_id)}</b>.  Текст: <b>{message.text}</b>',
                          message.chat.id, message_id_for_edit['activity_settings_menu'], reply_markup=keyboard())

    bot.delete_message(message.chat.id, message_id_for_edit['push_setting_text'])
    bot.delete_message(message.chat.id, message.id)


#Обработка "уведомления"->"получатели"
@bot.callback_query_handler(func=lambda call: re.match(r'[0-9]+_push=addresses',call.data))
def list_activity(call):
    user_id = get_user_id(call.message.chat.id)
    activity_id = call.data.split('_')[0]
    keyboard = make_keyboard_list_friend(user_id, activity_id=activity_id)
    #TODO нужно сделать кнопки навигации, чтобы иметь возможность вернуться к списку активностей
    bot.edit_message_text(formation_message_list_adresses(formation_list_adresses(activity_id)), call.message.chat.id, call.message.id, reply_markup=keyboard())


#Обработка "уведомления"->"получатели"-> "+"
@bot.callback_query_handler(func=lambda call: re.match(r'activity=[0-9]+_friend=add_friend',call.data))
def list_activity(call):
    message_id_for_edit['list_friend'] = call.message.id
    user_id = get_user_id(call.message.chat.id)
    activity_id = call.data.split('_')[0].split('=')[1]
    answer = bot.send_message(call.message.chat.id, 'Отправь следующим сообщением ник пользователя, которого хочешь добавить в друзья, @ печатать не надо')
    message_id_for_edit['info_add_friend'] = answer.id
    bot.register_next_step_handler(call.message, get_nick_new_friend, user_id, activity_id)


#"уведомления"->"получатели"-> "+" забираю ник из сообщения от пользователя
def get_nick_new_friend(message, user_id, activity_id):
    flug = add_friend(user_id, nick=message.text)
    bot.delete_message(message.chat.id, message.id)
    bot.delete_message(message.chat.id, message_id_for_edit['info_add_friend'])

    if flug:
        keyboard = make_keyboard_list_friend(user_id, activity_id)
        bot.edit_message_text(formation_message_list_adresses(formation_list_adresses(activity_id)), message.chat.id, message_id_for_edit['list_friend'], reply_markup=keyboard())

        if 'error_add_new_friend' in message_id_for_edit:
            bot.delete_message(message.chat.id, message_id_for_edit['error_add_new_friend'])

    else:
        error_add_friend = bot.send_message(message.chat.id, 'Не получилось добавить друга. Возможные причины: контакт уже у вас в друзьях, ошибка в нике,'
                                          ' пользователь с этим ником не зарегистрирован в боте')
        message_id_for_edit['error_add_new_friend'] = error_add_friend.id

        answer = bot.send_message(message.chat.id,
                                  'Отправь следующим сообщением ник пользователя, которого хочешь добавить в друзья, @ печатать не надо')

        message_id_for_edit['info_add_friend'] = answer.id
        bot.register_next_step_handler(message, get_nick_new_friend, user_id, activity_id)


#Обработка "уведомления"->"получатели"-> "имя_получателя"
#TODO нужно делать проверку на то, что сообщение нуждается в обновлении
@bot.callback_query_handler(func=lambda call: re.match(r'activity=[0-9]+_friend=[0-9]+',call.data))
def list_activity(call):
    friend_id = call.data.split('_')[1].split('=')[1]
    activity_id = call.data.split('_')[0].split('=')[1]
    user_id = get_user_id(call.message.chat.id)
    add_address(friend_id=friend_id, activity_id=activity_id)
    keyboard = make_keyboard_list_friend(user_id, activity_id)
    bot.edit_message_text(text=formation_message_list_adresses(formation_list_adresses(activity_id)),
                          chat_id=call.message.chat.id, message_id=call.message.id,
                          reply_markup=keyboard())



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
    user_row[call.message.chat.id].set_amount(0)
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
    finish_step_add_row(user_row[message.chat.id], message)


#Обрабатываем пропускание описания
@bot.callback_query_handler(func=lambda call: re.match(r'description=skip',call.data))
def callback_inline(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    user_row[call.message.chat.id].set_description('-')
    user_row[call.message.chat.id].set_date_added(date.today())
    finish_step_add_row(user_row[call.message.chat.id], call.message)


#Этап создания объекта Row и записи данных в БД
def finish_step_add_row(row_maker, message):
    row = row_maker.create_row()
    add_row(row)
    send_entery(row, message)


def send_entery(data_row:Row, message):
    notification_text = get_notification_text(data_row.activity_id)
    if notification_text == '-':
        notification_text = tg_entry_text(data_row)

    if '[количество]' in notification_text:
        notification_text = notification_text.replace('[количество]', str(data_row.amount))
    if notification_text:
        list_chat_id = formation_list_chat_id(data_row.activity_id)
        for chat_id in list_chat_id:
            bot.send_message(int(chat_id), notification_text)
    bot.send_message(message.chat.id, tg_entry_text(data_row) )



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    bot.send_message(call.message.chat.id, call.data)
if __name__ == '__main__':
    bot.infinity_polling(none_stop=True)