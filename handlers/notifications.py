from bot_instance import bot, message_id_for_edit
import re
from config import MESSAGE_TEXT

from models.activity import get_name_activity, update_notification_text, get_notification_text, formation_list_chat_id

from keyboards import make_keyboard_setting_push

from formation_text_message import setting_notification, tg_entry_text

from data_structares import Row

from handlers.utils import  add_message_id_to_user_data

#Обраотка нажатия на кнопку: "уведомления" из (удалить активность, уведомления, продолжить)
# Переход к настройке уведомлений выбранной активности
@bot.callback_query_handler(func=lambda call: re.match(r'activity_[0-9]+=push',call.data))
def open_notifications_settings(call):
    chat_id = call.message.chat.id
    activity_name = get_name_activity(call.data.split('=')[0].split('_')[1])
    activity_id = call.data.split('=')[0].split('_')[1]
    add_message_id_to_user_data(chat_id, 'activity_settings_menu', call.message.id)

    # TODO: сделать формирование текстового сообщения
    bot.edit_message_text(setting_notification(activity_id),
                          chat_id, call.message.id, reply_markup=keyboard())


# Обработка: "уведомления"->"текст уведомления"
# Запрос на ввод кастомного текста-шаблона уведомления для выбранной активности
@bot.callback_query_handler(func=lambda call: re.match(r'[0-9]+_push=text',call.data))
def start_setting_notification_text(call):
    chat_id = call.message.chat.id
    answer = bot.send_message(chat_id, MESSAGE_TEXT['example_push'])
    add_message_id_to_user_data(chat_id, 'push_setting_text', answer.id)
    activity_id = call.data.split('=')[0].split('_')[0]
    bot.register_next_step_handler(call.message, get_text_push, activity_id)


#Забираю текст уведомления от пользователя из сообщения
def get_text_push(message, activity_id):
    chat_id = call.message.chat.id
    update_notification_text(activity_id=activity_id, notification_text=message.text)
    keyboard = make_keyboard_setting_push(activity_id)
    bot.edit_message_text(f'Настройка текста уведомления и получателей уведомления для активности: <b>{get_name_activity(activity_id)}</b>.  Текст: <b>{message.text}</b>',
                          chat_id, message_id_for_edit[chat_id]['activity_settings_menu'], reply_markup=keyboard())
    #Todo заменить на remove_messages
    bot.delete_message(chat_id, message_id_for_edit[chat_id]['push_setting_text'])
    bot.delete_message(chat_id, message.id)




# Отправка уведомлений и сообщения пользователю о добавленной записи
def send_notifications(data_row:Row, message):
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