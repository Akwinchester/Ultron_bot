from bot_instance import bot, message_id_for_edit
from models.user import  add_friend, get_user_name, get_user_id, remove_friend
from models.activity import formation_message_list_adresses, formation_list_adresses, toggle_friend_in_recipient
from keyboards import make_keyboard_list_friend, make_keyboard_add_remove_friend
import re
from handlers.utils import add_message_id_to_user_data
from config import BUTTON_TEXT
from formation_text_message import list_name_friends


# Открытие главного меню работы со списком друзей
@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['friend'])
def open_main_menu(message):
    chat_id = message.chat.id
    user_id = get_user_id(chat_id)
    keyboard = make_keyboard_add_remove_friend()
    bot.delete_message(chat_id, message.id)
    bot.send_message(chat_id, list_name_friends(user_id), reply_markup=keyboard())


# Забираю ник из сообщения от пользователя
# Добавление нового получателя по нику
#Todo вынести текстовые сообщения в config.py
def add_friend_by_nick(message, user_id, activity_id):
    chat_id = message.chat.id
    nick = get_nick(message.text)
    flug = add_friend(user_id, nick=nick)
    bot.delete_message(chat_id, message.id)
    bot.delete_message(chat_id, message_id_for_edit[chat_id]['info_add_friend'])

    if flug:
        keyboard = make_keyboard_add_remove_friend()
        #ломается потому что нет ключа
        # bot.edit_message_text(chat_id, message_id_for_edit['list_friend_after_remove'], list_name_friends(user_id), reply_markup=keyboard())

        # keyboard = make_keyboard_list_friend(user_id, activity_id)
        # bot.edit_message_text(formation_message_list_adresses(formation_list_adresses(activity_id)), chat_id,
        #                       message_id_for_edit[chat_id]['list_friend'], reply_markup=keyboard())

        if 'error_add_new_friend' in message_id_for_edit[chat_id]:
            bot.delete_message(chat_id, message_id_for_edit[chat_id]['error_add_new_friend'])

    else:
        error_add_friend = bot.send_message(chat_id, 'Не получилось добавить друга. Возможные причины: контакт уже у вас в друзьях, ошибка в нике,'
                                          ' пользователь с этим ником не зарегистрирован в боте')
        add_message_id_to_user_data(chat_id, 'error_add_new_friend', error_add_friend.id)

        answer = bot.send_message(chat_id,
                                  'Отправь следующим сообщением ник пользователя, которого хочешь добавить в друзья, @ печатать не надо')

        add_message_id_to_user_data(chat_id, 'info_add_friend', answer.id)
        bot.register_next_step_handler(message, add_friend_by_nick, user_id, activity_id)


# Обработка "Мои друзья"-> "+"
# Запрос на ввод ника нового получателя, для добавления нового друга
@bot.callback_query_handler(func=lambda call: re.match(r'friend_list=add_friend',call.data))
def start_add_new_friend(call):
    chat_id = call.message.chat.id
    add_message_id_to_user_data(chat_id, 'list_friend', call.message.id)
    user_id = get_user_id(chat_id)
    answer = bot.send_message(chat_id, 'Отправь следующим сообщением ник пользователя, которого хочешь добавить в друзья. \nВ одном из форматов: \nhttps://t.me/ник \n@ник \nник')
    add_message_id_to_user_data(chat_id,'info_add_friend', answer.id)
    bot.register_next_step_handler(call.message, add_friend_by_nick, user_id, activity_id=None)


# Обработка "Мои друзья"-> "-"
@bot.callback_query_handler(func=lambda call: re.match(r'friend_list=remove_friend',call.data))
def start_remove_friend(call):
    chat_id = call.message.chat.id
    user_id = get_user_id(chat_id)
    keyboard = make_keyboard_list_friend(user_id, activity_id=None)
    add_message_id_to_user_data(chat_id, 'list_friend_after_remove', call.message.id)
    bot.edit_message_text('Выбери кого удалить из списка друзей', chat_id, call.message.id, reply_markup=keyboard())


#Удаление из друзей выбранного пользователя
@bot.callback_query_handler(func=lambda call: re.match(r'list_friends_[0-9]*=[0-9]*',call.data))
def handler_remove_friend(call):
    chat_id = call.message.chat.id
    user_id =  call.data.split('_')[2].split('=')[0]
    friend_id = call.data.split('_')[2].split('=')[1]
    remove_friend(user_id=user_id, friend_id=friend_id)
    keyboard = make_keyboard_list_friend(user_id, activity_id=None)
    bot.edit_message_text('Выбери кого удалить из списка друзей', chat_id, call.message.id, reply_markup=keyboard())


def get_nick(message_text):
    # Паттерн для поиска никнейма Телеграмма после "t.me/" или "@"
    pattern = r"(?:t\.me\/|@)(\w+)"

    match = re.search(pattern, message_text)
    if match:
        return match.group(1)
    return message_text  # Если совпадение не найдено, возвращаем исходный текст

#TODO реализовать удаление адресата из списка

#TODO реализовать удаление из друзей