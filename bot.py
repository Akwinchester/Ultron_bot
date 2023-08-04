from bot_instance import bot, message_id_for_edit

from handlers.auth import processing_registration_selection, get_and_check_username, get_and_check_password

from handlers.main_commands import send_welcome_message, open_main_menu, handle_cancel_button

from handlers.utils import remove_messages


from handlers.activities import open_settings_activities, display_archived_activities,display_friend_activities,\
    clone_activity_friend, start_activity_creation, get_name_new_activity, add_activity_from_archive, open_activity_menu,\
    delete_selected_activity, open_activity_selection_for_entry

from handlers.friends import add_friend_by_nick, setting_recipient_list, add_friend_in_recipient, start_add_new_friend

from handlers.notifications import open_notifications_settings, start_setting_notification_text

from handlers.entry import start_add_entry, request_amount_input, skip_amount_input,\
    request_description_input, skip_description

# Обработчик коллбэков без явного соответствия
@bot.callback_query_handler(func=lambda call: True)
def process_callback(call):
    bot.send_message(call.message.chat.id, call.data)

if __name__ == '__main__':
    bot.infinity_polling(none_stop=True)


#Что нужно сделать:


#TODO Вынести все текстовые сообщения и именя кнопок в файлы config.py и formation_text_message.py в свловарь с осмысленными и читабельными ключами

#TODO сделать аннотации ко всем функциям(кроме обработчиков, которые принимают call или message без доп аргументов) типы получаемых данных, типы возвращаемых данных

#TODO сделать ревью кода с помощью GPT: добавить блоки try: except: где это необходимо, ренейминг, привести к единому стилю, привести в должный вид import-ы

#TODO сделать логирование ошибок и основных событий в боте: (добавление пользователя, создание активности, добавление друзей)

#TODO подуать нужны ли тесты и если нужны, сделать