from keyboa import Keyboa
from telebot import types
from config import BUTTON_TEXT
from models.activity import formation_list_activity

def make_keyboard_start():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton(BUTTON_TEXT['start'])
    markup.add(button1)
    return markup


def make_keyboard_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    button1 = types.KeyboardButton(BUTTON_TEXT['add_row'])
    button2 = types.KeyboardButton(BUTTON_TEXT['shere_friends'])
    button3 = types.KeyboardButton(BUTTON_TEXT['information'])
    button4 = types.KeyboardButton(BUTTON_TEXT['help'])
    button5 = types.KeyboardButton(BUTTON_TEXT['To_do'])
    button6 = types.KeyboardButton(BUTTON_TEXT['text_training'])

    markup.add(button1, button2)
    markup.add(button3, button4)
    markup.add(button5, button6)

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


def make_keyboard_setting_push():
    items = [('Текст уведомления', 'text'), ('Получатели', 'addresses'), ('Список активностей', 'save')]
    keyboard = Keyboa(items=items, items_in_row=2, front_marker='push=')
    return keyboard