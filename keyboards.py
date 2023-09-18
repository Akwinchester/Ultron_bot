from keyboa import Keyboa
from telebot import types
from config import BUTTON_TEXT
from models.activity import formation_list_activity
from models.user import get_list_friend


def make_keyboard_check_registration():
    items = [('Зарегистрирован на сайте', '1'), ('Не зарегистрирован на сайте', '0'), ('❌', 'close_window')]
    keyboard = Keyboa(items=items, items_in_row=2, front_marker='check_registration=')
    return keyboard


def make_keyboard_start():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton(BUTTON_TEXT['start'])
    markup.add(button1)
    return markup


def make_keyboard_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    button1 = types.KeyboardButton(BUTTON_TEXT['add_row'])
    button2 = types.KeyboardButton(BUTTON_TEXT['friend'])
    button3 = types.KeyboardButton(BUTTON_TEXT['help'])

    markup.add(button1)
    markup.add(button2)
    markup.add(button3)


    return markup


def make_keyboard_list_activity(user_id, status):
    items = formation_list_activity(user_id, status)
    if status==1:
        items.append(('+', 'add_activity'))
    items.append(('❌', 'close_window'))
    keyboard = Keyboa(items=items, items_in_row=2, front_marker='activity=')
    return keyboard


def make_keyboard_list_activity_for_change_status(user_id, status):
    items = formation_list_activity(user_id, status)
    items.append(('Список активностей','list_activity'))
    items.append(('❌', 'close_window'))
    keyboard = Keyboa(items=items, items_in_row=2, front_marker='activity=change_status=')
    return keyboard


def make_keyboard_skip_amount():
    items=[('Пропустить', 'skip'), ('❌', 'close_window')]
    keyboard = Keyboa(items=items, items_in_row=2, front_marker='amount=')
    return keyboard


def make_keyboard_skip_description():
    items = [('Пропустить', 'skip'), ('❌', 'close_window')]
    keyboard = Keyboa(items=items, items_in_row=2, front_marker='description=')
    return keyboard


def make_keyboard_setting_activity(activity_id):
    items = [('Удалить активность', 'delete'), ('Уведомления', 'push'), ('Список активностей','list_activity'), ('Продолжить', 'continue'), ('❌', 'close_window')]
    keyboard = Keyboa(items=items, items_in_row=2, front_marker=f'activity_{activity_id}=')
    return keyboard


def make_keyboard_setting_push(activity_id):
    items = [('Текст уведомления', 'text'), ('Получатели', 'addresses'), ('Список активностей', 'list_activity'), ('❌', 'close_window')]
    keyboard = Keyboa(items=items, items_in_row=2, front_marker=f'{activity_id}_push=')
    return keyboard


def make_keyboard_list_friend(user_id, activity_id):
    friends = get_list_friend(user_id)
    items = []
    for f in friends:
        if f:
            items.append((f['name'], f['id']))
    items.append(('Список активностей', 'list_activity'))
    items.append(('❌', 'close_window'))

    if activity_id==None:
        keyboard = Keyboa(items=items, items_in_row=2, front_marker=f'list_friends_{user_id}=')
    else:
        keyboard = Keyboa(items=items, items_in_row=2, front_marker=f'activity={activity_id}_friend=')
    return keyboard


def make_keyboard_add_new_or_friend_activity(user_id):
    friends = get_list_friend(user_id)
    items = []
    items.append(('🔙', 'list_activity'))
    items.append(('мои активности', 'my_activity'))

    for f in friends:
        if f:
            items.append((f['name'], 'show_list_activity_friend='+ str(f['id'])))
    items.append(('❌', 'close_window'))
    keyboard = Keyboa(items=items, items_in_row=2, front_marker=f'activity=')
    return keyboard


def make_keyboard_list_activity_friend(friend_id):
    items = formation_list_activity(friend_id)
    items.append(('🔙', 'list_activity'))
    items.append(('❌', 'close_window'))
    keyboard = Keyboa(items=items, items_in_row=2, front_marker=f'activity=add_friend={friend_id}_activity=')
    return keyboard


def make_keyboard_add_remove_friend():
    items = [('+', 'add_friend'),('-', 'remove_friend'),('❌', 'close_window')]
    keyboard = Keyboa(items=items, items_in_row=2, front_marker=f'friend_list=')
    return keyboard
