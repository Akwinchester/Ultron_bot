from bot_instance import bot, message_id_for_edit
from models.user import  add_friend, get_user_name, get_user_id, remove_friend
from models.activity import formation_message_list_adresses, formation_list_adresses, toggle_friend_in_recipient
from keyboards import make_keyboard_list_friend, make_keyboard_add_remove_friend
import re
from handlers.utils import add_message_id_to_user_data
from config import BUTTON_TEXT
from formation_text_message import list_name_friends


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


# Обработка: "уведомления"->"получатели"-> "имя_получателя"
# Добавление выбранного друга в список получателей уведомлений по выбранной активности
#TODO нужно делать проверку на то, что сообщение нуждается в обновлении. Чтобы не падала ошибка, что старое и новое содержимое идентично
#TODO реализовать удаление адресата из списка
@bot.callback_query_handler(func=lambda call: re.match(r'activity=[0-9]+_friend=[0-9]+',call.data))
def toggle_friend_in_recipient_handler(call):
    chat_id = call.message.chat.id
    friend_id = call.data.split('_')[1].split('=')[1]
    activity_id = call.data.split('_')[0].split('=')[1]
    user_id = get_user_id(chat_id)

    toggle_friend_in_recipient(friend_id=friend_id, activity_id=activity_id)

    keyboard = make_keyboard_list_friend(user_id, activity_id)
    bot.edit_message_text(text=formation_message_list_adresses(formation_list_adresses(activity_id)),
                          chat_id=chat_id, message_id=call.message.id,
                          reply_markup=keyboard())

