from bot_instance import bot
from keyboards import make_keyboard_check_registration, make_keyboard_main_menu
from config import MESSAGE_TEXT, BUTTON_TEXT


# Приветственное сообщение с клавиатурой: "Зарегистрирован" or "Не зарегистрирован"
@bot.message_handler(commands=['start'])
def send_welcome_message(message):
    keyboard = make_keyboard_check_registration()
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!!!\n' + MESSAGE_TEXT['start'],
                     reply_markup=keyboard())
    create_user(message.from_user.first_name, message.chat.id, message.from_user.username)


# Открытие главного меню
@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['start'])
def open_main_menu(message):
    bot.send_message(message.chat.id, MESSAGE_TEXT['main_menu'], reply_markup=make_keyboard_main_menu())


# Возвращение в главное меню через кнопку отмены
@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['cancel'])
def handle_cancel_button(message):
    bot.send_message(message.chat.id, MESSAGE_TEXT['main_menu'], reply_markup=make_keyboard_main_menu())


