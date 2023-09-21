from bot_instance import bot, message_id_for_edit
from keyboards import make_keyboard_check_registration, make_keyboard_add_new_or_friend_activity,\
    make_keyboard_list_activity_friend, make_keyboard_list_activity, make_keyboard_list_activity_for_change_status, make_keyboard_setting_activity
from config import MESSAGE_TEXT, BUTTON_TEXT

from models.user import get_user_id, get_user_name
from models.activity import create_activity_for_template, add_activity, change_status_activity, delete_activity

from formation_text_message import list_activity_True, select_activity
import re
from handlers.utils import add_message_id_to_user_data, remove_messages


# Обработка нажатия кнопки добавлене активности "добавить запись"->"+"
# Открытие меню выбора создания или подключения активности
@bot.callback_query_handler(func=lambda call: call.data == 'activity=add_activity')
def open_settings_activities(call):
    chat_id = call.message.chat.id
    user_id = get_user_id(chat_id)
    keyboard = make_keyboard_add_new_or_friend_activity(user_id)

    if 'add_activity' in message_id_for_edit[chat_id]:
        bot.edit_message_text(list_activity_True(user_id), call.message.chat.id, message_id_for_edit[chat_id]['add_activity'],
                              reply_markup=keyboard())
    else:
        answer = bot.send_message(chat_id, list_activity_True(user_id), reply_markup=keyboard())
        add_message_id_to_user_data(chat_id,'add_activity',answer.message_id)
        add_message_id_to_user_data(chat_id, 'list_activity', call.message.id)
    bot.register_next_step_handler(call.message, get_name_new_activity)


# Обработка нажатия кнопки добавлене активности "добавить запись"->"+"->"имя пользователя".
# Отображение списка активностей выбранного пользователя
@bot.callback_query_handler(func=lambda call: re.match(r'activity=show_list_activity_friend=[0-9]+',call.data))
def display_friend_activities(call):
    chat_id = call.message.chat.id
    bot.clear_step_handler_by_chat_id(chat_id)
    friend_id = call.data.split('=')[2]
    friend_name = get_user_name(friend_id)
    keyboard = make_keyboard_list_activity_friend(friend_id)
    bot.edit_message_text(f'Активности пользователя {friend_name}',  chat_id, message_id_for_edit[chat_id]['add_activity'], reply_markup=keyboard())


# Обработка нажатия кнопки добавлене активности "добавить запись"->"+"->"имя пользователя"->"название активности".
# Создание дубликата активности по шаблону активности друга, для возможности участвовать в соревновании по данной активности.
@bot.callback_query_handler(func=lambda call: re.match(r'activity=add_friend=[0-9]+_activity=[0-9]+',call.data))
def clone_activity_friend(call):
    chat_id = call.message.chat.id
    user_id = get_user_id(chat_id)
    activity_id = call.data.split('=')[3]
    create_activity_for_template(user_id=user_id, activity_id=activity_id)
    keyboard = make_keyboard_add_new_or_friend_activity(user_id)
    bot.edit_message_text(list_activity_True(user_id), call.message.chat.id,
                          message_id_for_edit[chat_id]['add_activity'],
                          reply_markup=keyboard())


#Получение имени новой активности от пользователя из сообщения
#Создание активности из полученного имени активности
def get_name_new_activity(message):
    chat_id = message.chat.id
    add_activity(chat_id, name_activity=message.text)
    user_id = get_user_id(message.chat.id)
    keyboard = make_keyboard_list_activity(user_id, status=1)
    #Todo заменить на remove_messages

    bot.delete_message(chat_id, message.id)
    bot.edit_message_text(text='Выбери или создай активность', chat_id=chat_id, message_id=message_id_for_edit[chat_id]['add_activity'], reply_markup=keyboard())


# Обработка нажатия кнопки добавлене активности "добавить запись"->"+"->"мои активности"
# Отображение неактивных активностей пользователя
@bot.callback_query_handler(func=lambda call: call.data == 'activity=my_activity')
def display_archived_activities(call):
    chat_id = call.message.chat.id
    bot.clear_step_handler_by_chat_id(chat_id)
    user_id = get_user_id(chat_id)
    keyboard = make_keyboard_list_activity_for_change_status(user_id=user_id, status=0)
    bot.edit_message_text(f'Неактивные активности', chat_id,
                          message_id_for_edit[chat_id]['add_activity'], reply_markup=keyboard())


# Смена статуса активности "добавить запись"->"+"->"мои активности"->"название активности"
# Смена статуса выбранной активности c "архивная" на "актуальная"
@bot.callback_query_handler(func=lambda call: re.match(r'activity=change_status=[0-9]',call.data))
def add_activity_from_archive(call):
    activity_id = call.data.split('=')[2]
    change_status_activity(activity_id)


# Обработка нажатия на кнопку: "Добавить запись"->"имя_активности"
# Отображение меню настроек выбранной активности
@bot.callback_query_handler(func=lambda call: re.match(r'activity=[0-9]+\b',call.data))
def open_activity_menu(call):
    chat_id = call.message.chat.id
    activity_id = call.data.split('=')[1]
    add_message_id_to_user_data(chat_id, 'list_activity', call.message.id)
    keyboard = make_keyboard_setting_activity(activity_id)
    bot.edit_message_text(select_activity(activity_id), chat_id, call.message.id, reply_markup=keyboard())


# Обработка: "уведомления"->"список активностей"
# Обработка: "имя_активности"->"список активностей"
# Обработка: "добавить запись"->"+"->"имя пользователя"->"<<<<".
# Возврат к списку актуальных активностей из позиций: список активностей друга, настройка уведомления, меню выбранной активности
@bot.callback_query_handler(func=lambda call: re.match(r'.*=list_activity$',call.data))
def back_to_current_activities(call):
    user_id = get_user_id(call.message.chat.id)
    keyboard = make_keyboard_list_activity(user_id, status=1)
    bot.edit_message_text('Выбери или создай активность', call.message.chat.id, call.message.id, reply_markup=keyboard())


# Обработка нажатия на кнопку: "Добавить запись"->"имя_активности"->"Удалить активность"
# Удаление выбранной активности
@bot.callback_query_handler(func=lambda call: re.match(r'activity_[0-9]+=delete',call.data))
def delete_selected_activity(call):
    activity_id = call.data.split('=')[0].split('_')[1]
    delete_activity(activity_id)
    user_id = get_user_id(call.message.chat.id)
    keyboard = make_keyboard_list_activity(user_id, status=1)
    bot.edit_message_text('Выбери или создай активность',call.message.chat.id, call.message.id, reply_markup=keyboard())


# Обработка нажатия кнопки "Добавить запись"
# Переход к выбору активности для новой записи
@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['add_row'])
def open_activity_selection_for_entry(message):
    chat_id = message.chat.id
    bot.delete_message(chat_id, message.id)
    user_id = get_user_id(chat_id)
    keyboard = make_keyboard_list_activity(user_id, status=1)
    answer = bot.send_message(chat_id, 'Выбери или создай активность', reply_markup=keyboard())
    add_message_id_to_user_data(chat_id, 'add_activity', answer.message_id)