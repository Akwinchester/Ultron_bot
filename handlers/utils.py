from bot_instance import  bot, message_id_for_edit
import json

# Функция удаление сообщений бота и пользователя по идентификаторам
def remove_messages(chat_id, list_key:list):
    for key in list_key:
        if key in message_id_for_edit[chat_id]:
            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id_for_edit[chat_id][key])
                del message_id_for_edit[chat_id][key]
            except:
                print(f'Ошибка удаления сообщения - {key} с id:', message_id_for_edit[chat_id][key], 'в чате с id:', chat_id)


def add_message_id_to_user_data(chat_id, key, value):
    if chat_id not in message_id_for_edit:
        message_id_for_edit[chat_id] = {}
    message_id_for_edit[chat_id][key] = value


# edit_message()