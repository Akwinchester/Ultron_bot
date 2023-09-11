from bot_instance import bot
from handlers.utils import remove_messages, add_message_id_to_user_data
from models.user import check_user_name_bd, update_user, create_user

from keyboards import make_keyboard_check_registration, make_keyboard_main_menu
from config import MESSAGE_TEXT
from werkzeug.security import check_password_hash
import re


# Обработка ответа пользователя с клавиатуры: "Зарегистрирован" or "Не зарегистрирован"
@bot.callback_query_handler(func=lambda call: re.match(r'check_registration=[0-1]',call.data))
def processing_registration_selection(call):
    chat_id = call.message.chat.id
    status = call.data.split('=')[1]
    if status == '1':
        answer = bot.send_message(chat_id, MESSAGE_TEXT['authorized'])
        add_message_id_to_user_data(chat_id, 'check_authorization', answer.id)
        bot.register_next_step_handler(call.message, get_and_check_username)

    elif status == '0':
        answer = bot.send_message(chat_id, MESSAGE_TEXT['no_authorized'])
        add_message_id_to_user_data(chat_id, 'check_authorization', answer.id)
        create_user(message.from_user.first_name, chat_id, message.from_user.username)



# Забираем из сообщения username и проверяем есть ли имя пользователя в БД
def get_and_check_username(message):
    chat_id = message.chat.id
    remove_messages(message, ['check_authorization_True', 'check_authorization_False', 'user_name'])
    add_message_id_to_user_data(chat_id, 'user_name', message.id)
    user = check_user_name_bd(message.text)
    if user:
        answer = bot.send_message(chat_id, f'Отлично пользователь с именем {message.text} найден в системе. Отправь следующим сообщением пароль')
        add_message_id_to_user_data(chat_id, 'check_authorization_True', answer.id)
        remove_messages(chat_id, ['check_authorization'])
        bot.register_next_step_handler(message, get_and_check_password, user)

    else:
        answer = bot.send_message(message.chat.id, 'Сожалею, но пользователь не найден. Проверь написание и отправь сообщение с именем еще раз.')
        add_message_id_to_user_data(chat_id, 'check_authorization_False', answer.id)
        bot.register_next_step_handler(message, get_and_check_username)


# Забираем из сообщения пароль и сравниваем с хешем пароля из БД
def get_and_check_password(message, user):
    remove_messages(message, ['user_name', 'password_False', 'check_authorization_True'])

    if check_password_hash(user.password, message.text):
        update_user(user_name=user.username, real_name=message.from_user.first_name,
                    chat_id=message.chat.id, nick=message.from_user.username)
        bot.send_message(message.chat.id, 'Поздравляю, вы вошли в систему. Ваши аккаунты на сайте и в боте синхронизированы.', reply_markup=make_keyboard_main_menu())
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    else:
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
        answer = bot.send_message(message.chat.id, "Увы, пароль неверный. Отправь сообщением верный пароль")
        add_message_id_to_user_data(chat_id, 'password_False', answer.id)
        bot.register_next_step_handler(message, get_and_check_password, user)
