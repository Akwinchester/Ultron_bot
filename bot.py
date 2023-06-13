import telebot
from config import BOT_TOKEN, MESSAGE_TEXT, BUTTON_TEXT
from models.user import create_user
from models.activity import formation_list_activity, add_activity
from keyboards import make_keyboard_start, make_keyboard_main_menu, make_keyboard_list_activity

from dataclasses import dataclass
from datetime import date
from keyboa import Keyboa


message_id_for_edit = {}
@dataclass
class Row:
    date_added: date
    activity: str
    amount: int
    description: str
    # text_notification: str


class RowFactory:
    def __init__(self):
        self.data = {}

    def set_date_added(self, date_added: date):
        self.data['date_added'] = date_added

    def set_activity(self, activity: str):
        self.data['activity'] = activity

    def set_amount(self, amount: int):
        self.data['amount'] = amount

    def set_description(self, description: str):
        self.data['description'] = description

    def create_row(self) -> Row:
        return Row(**self.data)



bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!!!\n'+MESSAGE_TEXT['start'],
                     reply_markup=make_keyboard_start())

    create_user(message.from_user.first_name, message.chat.id)


@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['start'])
def start_button(message):
    bot.send_message(message.chat.id, MESSAGE_TEXT['main_menu'], reply_markup=make_keyboard_main_menu())


@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['cancel'])
def cancel_button(message):
    bot.send_message(message.chat.id, MESSAGE_TEXT['main_menu'], reply_markup=make_keyboard_main_menu())


@bot.message_handler(content_types=['text'], regexp=BUTTON_TEXT['add_row'])
def one_button(message):
    keyboard = make_keyboard_list_activity(message.chat.id)
    bot.send_message(message.chat.id, 'Выбери', reply_markup=keyboard())


@bot.callback_query_handler(func=lambda call: call.data == 'activity=add_activity')
def callback_inline(call):
    answer = bot.send_message(call.message.chat.id, 'отправь название новой активности следующим сообщением')
    message_id_for_edit['list_activity'] = call.message.id
    message_id_for_edit['name_activity'] = answer.message_id
    bot.register_next_step_handler(call.message, get_name_new_activity)


def get_name_new_activity(message):
    chat_id = message.chat.id
    add_activity(chat_id, name_activity=message.text)

    keyboard = make_keyboard_list_activity(chat_id)
    bot.delete_message(chat_id, message.id)
    bot.delete_message(chat_id, message_id_for_edit['name_activity'])
    bot.edit_message_text(text='Выбери:', message_id=message_id_for_edit['list_activity'],
                          chat_id=message.chat.id,
                          reply_markup=keyboard())


if __name__ == '__main__':
    bot.infinity_polling(none_stop=True)