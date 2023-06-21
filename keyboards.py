from keyboa import Keyboa
from telebot import types
from config import BUTTON_TEXT
from models.activity import formation_list_activity
from models.user import get_list_friend

def make_keyboard_start():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton(BUTTON_TEXT['start'])
    markup.add(button1)
    return markup


def make_keyboard_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    button1 = types.KeyboardButton(BUTTON_TEXT['add_row'])
    button3 = types.KeyboardButton(BUTTON_TEXT['information'])
    button4 = types.KeyboardButton(BUTTON_TEXT['help'])

    markup.add(button1)
    markup.add(button3)
    markup.add(button4)

    return markup


def make_keyboard_list_activity(chat_id):
    items = formation_list_activity(chat_id)
    items.append(('+', 'add_activity'))
    keyboard = Keyboa(items=items, items_in_row=2, front_marker='activity=')
    return keyboard


def make_keyboard_skip_amount():
    items=[('Пропустить', 'skip'), ('Указать', 'continue')]
    keyboard = Keyboa(items=items, items_in_row=2, front_marker='amount=')
    return keyboard


def make_keyboard_skip_description():
    items=[('Пропустить', 'skip'), ('Указать', 'continue')]
    keyboard = Keyboa(items=items, items_in_row=2, front_marker='description=')
    return keyboard


def make_keyboard_setting_activity(activity_id):
    items = [('Удалить активность', 'delete'), ('Уведомления', 'push'), ('Список активностей','list_activity'), ('Продолжить', 'continue')]
    keyboard = Keyboa(items=items, items_in_row=2, front_marker=f'activity_{activity_id}=')
    return keyboard


def make_keyboard_setting_push(activity_id):
    items = [('Текст уведомления', 'text'), ('Получатели', 'addresses'), ('Список активностей', 'save')]
    keyboard = Keyboa(items=items, items_in_row=2, front_marker=f'{activity_id}_push=')
    return keyboard


def make_keyboard_list_friend(user_id, activity_id):
    friends = get_list_friend(user_id)
    items = []
    for f in friends:
        if f:
            items.append((f.name, f.id))
    items.append(('список активностей', 'list_activity'))
    items.append(('+', 'add_friend'))
    keyboard = Keyboa(items=items, items_in_row=2, front_marker=f'activity={activity_id}_friend=')
    return keyboard