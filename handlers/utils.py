from bot_instance import  bot, message_id_for_edit

# Функция удаление сообщений бота и пользователя по идентификаторам
def remove_messages(message, list_key:list):
    for key in list_key:
        if key in message_id_for_edit:
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=message_id_for_edit[key])
                del message_id_for_edit[key]
            except:
                print(f'Ошибка удаления сообщения - {key} с id:', message_id_for_edit[key], 'в чате с id:', message.chat.id)