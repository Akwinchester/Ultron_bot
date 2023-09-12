from bot_instance import bot, message_id_for_edit, user_row
import re
from data_structares import Row, RowFactory
from keyboards import make_keyboard_skip_amount, make_keyboard_skip_description
from models.entry import add_row
from handlers.notifications import send_notifications
from datetime import date
from handlers.utils import add_message_id_to_user_data


# Обработка: "Добавить запись"->"название активности"
# Выбор: клавиатура "указывать количественную характеристику or пропустить"
@bot.callback_query_handler(func=lambda call: re.match(r'activity_[0-9]+=continue',call.data))
def start_add_entry(call):
    chat_id = call.message.chat.id
    activity_id = call.data.split('=')[0].split('_')[1]
    bot.delete_message(chat_id, message_id_for_edit[chat_id]['list_activity'])
    user_row[chat_id] = RowFactory()
    user_row[chat_id].set_activity_id(activity_id)
    keyboard = make_keyboard_skip_amount()
    answer = bot.send_message(chat_id, 'Можешь указать количественную характеристику', reply_markup=keyboard())
    add_message_id_to_user_data(chat_id, 'get_amount', answer.id)
    bot.register_next_step_handler(call.message, get_amount)


# # Запрос на ввод количественного значения
# @bot.callback_query_handler(func=lambda call: re.match(r'amount=continue',call.data))
# def request_amount_input(call):
#     chat_id = call.message.chat.id
#     bot.delete_message(call.message.chat.id, call.message.id)
#     answer = bot.send_message(call.message.chat.id, 'Отправь количество следующим сообщением')
#     message_id_for_edit[chat_id]['amount_continue'] = answer.id
#     bot.register_next_step_handler(call.message, get_amount)



#Получение количественной характеристики от пользователя из сообщения
def get_amount(message):
    chat_id = message.chat.id
    user_row[chat_id].set_amount(int(message.text))
    bot.delete_message(chat_id=chat_id, message_id=message_id_for_edit[chat_id]['get_amount'])
    bot.delete_message(chat_id, message.id)

    keyboard = make_keyboard_skip_description()
    answer = bot.send_message(chat_id, 'Можешь добавить описание', reply_markup=keyboard())
    add_message_id_to_user_data(chat_id, 'description_cskip', answer.id)
    bot.register_next_step_handler(message, get_description)


# Пропускаем ввод количественной характеристики
# Переход к вводу описания с пропуском значения
@bot.callback_query_handler(func=lambda call: re.match(r'amount=skip',call.data))
def skip_amount_input(call):
    chat_id = call.message.chat.id
    bot.clear_step_handler_by_chat_id(chat_id)
    bot.delete_message(call.message.chat.id, call.message.id)
    user_row[chat_id].set_amount(0)
    keyboard = make_keyboard_skip_description()
    bot.send_message(chat_id, 'Можешь добавить описание', reply_markup=keyboard())
    bot.register_next_step_handler(call.message, get_description)



# # Запрос на ввод описания записи
# @bot.callback_query_handler(func=lambda call: re.match(r'description=continue',call.data))
# def request_description_input(call):
#     chat_id = call.message.chat.id
#     answer = bot.send_message(call.message.chat.id, 'Отправь описание следующим сообщением')
#     message_id_for_edit[chat_id]['description_cskip'] = answer.id
#
#     bot.delete_message(call.message.chat.id, call.message.id)
#     bot.register_next_step_handler(call.message, get_description)


#Получение описания от пользователя из сообщения
def get_description(message):
    chat_id = message.chat.id
    user_row[chat_id].set_description(message.text)
    user_row[chat_id].set_date_added(date.today())
    bot.delete_message(chat_id, message.id)
    bot.delete_message(chat_id, message_id_for_edit[chat_id]['description_cskip'])
    create_and_save_entry(user_row[chat_id], message)


#Обрабатываем пропускание описания
@bot.callback_query_handler(func=lambda call: re.match(r'description=skip',call.data))
def skip_description(call):
    chat_id = call.message.chat.id
    bot.clear_step_handler_by_chat_id(chat_id)
    bot.delete_message(chat_id, call.message.id)
    user_row[chat_id].set_description('-')
    user_row[chat_id].set_date_added(date.today())
    create_and_save_entry(user_row[chat_id], call.message)


#Этап создания объекта Row и записи данных в БД
def create_and_save_entry(row_maker, message):
    row = row_maker.create_row()
    add_row(row)
    send_notifications(row, message)