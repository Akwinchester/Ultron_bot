from bot_instance import bot, message_id_for_edit
from models.user import  add_friend, get_user_name, get_user_id
from models.activity import formation_message_list_adresses, formation_list_adresses, add_address
from keyboards import make_keyboard_list_friend, make_keyboard_add_remove_friend
import re
from handlers.utils import add_message_id_to_user_data
from config import BUTTON_TEXT


# Открытие главного меню работы со списком друзей
@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['friend'])
def open_main_menu(message):
    chat_id = message.chat.id
    keyboard = make_keyboard_add_remove_friend()
    bot.delete_message(chat_id, message.id)
    bot.send_message(chat_id, 'список друзей', reply_markup=keyboard())



# Обработка: "уведомления"->"получатели"-> "+"
# Забираю ник из сообщения от пользователя
# Добавление нового получателя по нику
#Todo вынести текстовые сообщения в config.py
def add_friend_by_nick(message, user_id, activity_id):
    chat_id = message.chat.id
    flug = add_friend(user_id, nick=message.text)
    bot.delete_message(chat_id, message.id)
    bot.delete_message(chat_id, message_id_for_edit[chat_id]['info_add_friend'])

    if flug:
        keyboard = make_keyboard_list_friend(user_id, activity_id)
        bot.edit_message_text(formation_message_list_adresses(formation_list_adresses(activity_id)), chat_id,
                              message_id_for_edit[chat_id]['list_friend'], reply_markup=keyboard())

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



# Обработка "уведомления"->"получатели"
# Показ и настройка списка текущих получателей уведомлений
@bot.callback_query_handler(func=lambda call: re.match(r'[0-9]+_push=addresses',call.data))
def setting_recipient_list(call):
    chat_id = call.message.chat.id
    user_id = get_user_id(chat_id)
    activity_id = call.data.split('_')[0]
    keyboard = make_keyboard_list_friend(user_id, activity_id=activity_id)
    #TODO нужно сделать кнопки навигации, чтобы иметь возможность вернуться к списку активностей
    bot.edit_message_text(formation_message_list_adresses(formation_list_adresses(activity_id)), chat_id,
                          call.message.id, reply_markup=keyboard())


# Обработка "Мои друзья"-> "+"
# Запрос на ввод ника нового получателя, для добавления нового друга
@bot.callback_query_handler(func=lambda call: re.match(r'friend_list=add_friend',call.data))
def start_add_new_friend(call):
    chat_id = call.message.chat.id
    add_message_id_to_user_data(chat_id, 'list_friend', call.message.id)
    user_id = get_user_id(chat_id)
    answer = bot.send_message(chat_id, 'Отправь следующим сообщением ник пользователя, которого хочешь добавить в друзья, @ печатать не надо')
    add_message_id_to_user_data(chat_id,'info_add_friend', answer.id)
    bot.register_next_step_handler(call.message, add_friend_by_nick, user_id, activity_id=None)


# Обработка: "уведомления"->"получатели"-> "имя_получателя"
# Добавление выбранного друга в список получателей уведомлений по выбранной активности
#TODO нужно делать проверку на то, что сообщение нуждается в обновлении. Чтобы не падала ошибка, что старое и новое содержимое идентично
#TODO реализовать удаление адресата из списка
@bot.callback_query_handler(func=lambda call: re.match(r'activity=[0-9]+_friend=[0-9]+',call.data))
def add_friend_in_recipient(call):
    chat_id = call.message.chat.id
    friend_id = call.data.split('_')[1].split('=')[1]
    activity_id = call.data.split('_')[0].split('=')[1]
    user_id = get_user_id(chat_id)
    add_address(friend_id=friend_id, activity_id=activity_id)
    keyboard = make_keyboard_list_friend(user_id, activity_id)
    bot.edit_message_text(text=formation_message_list_adresses(formation_list_adresses(activity_id)),
                          chat_id=chat_id, message_id=call.message.id,
                          reply_markup=keyboard())


# Обработка "Мои друзья"-> "-"
@bot.callback_query_handler(func=lambda call: re.match(r'friend_list=remove_friend',call.data))
def start_add_new_friend(call):
    chat_id = call.message.chat.id
    user_id = get_user_id(chat_id)
    keyboard = make_keyboard_list_friend(user_id, activity_id=None)
    bot.edit_message_text('Выбери кого удалить из списка друзей', chat_id, call.message.id, reply_markup=keyboard())


# Обработка "уведомления"->"получатели"-> "❌"
@bot.callback_query_handler(func=lambda call: re.match(r'.*=close_window$',call.data))
def start_add_new_friend(call):
    chat_id = call.message.chat.id
    bot.clear_step_handler_by_chat_id(chat_id)
    bot.delete_message(chat_id, call.message.id)
#TODO реализовать удаление адресата из списка

#TODO реализовать удаление из друзей