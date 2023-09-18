from bot_instance import bot
from keyboards import make_keyboard_check_registration, make_keyboard_main_menu
from config import MESSAGE_TEXT, BUTTON_TEXT
from models.user import create_user
from logger import logger
from handlers.utils import add_message_id_to_user_data
import re


# Приветственное сообщение с клавиатурой: "Зарегистрирован" or "Не зарегистрирован"
@bot.message_handler(commands=['start'])
def send_welcome_message(message):
    chat_id = message.chat.id
    keyboard = make_keyboard_check_registration()
    answer = bot.send_message(chat_id, f'Привет, {message.from_user.first_name}!!!\n' + MESSAGE_TEXT['start'],
                     reply_markup=keyboard())
    add_message_id_to_user_data(chat_id, 'after_start_bot', answer.id )
    bot.delete_message(chat_id, message_id=message.id)
    logger.info(f'Пользователь с chat_id: {message.chat.id} использовал команду /start')


# Открытие главного меню
@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['start'])
def open_main_menu(message):
    bot.send_message(message.chat.id, MESSAGE_TEXT['main_menu'], reply_markup=make_keyboard_main_menu())
    logger.info(f'Пользователь {message.chat.id} использовал "Главное меню"')


# Возвращение в главное меню через кнопку отмены
@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['cancel'])
def handle_cancel_button(message):
    bot.send_message(message.chat.id, MESSAGE_TEXT['main_menu'], reply_markup=make_keyboard_main_menu())
    logger.info(f'Пользователь {message.chat.id} использовал "cancel"')


# Обработка ... -> "❌"
@bot.callback_query_handler(func=lambda call: re.match(r'.*=close_window$',call.data))
def close_windows(call):
    chat_id = call.message.chat.id
    bot.clear_step_handler_by_chat_id(chat_id)
    bot.delete_message(chat_id, call.message.id)
