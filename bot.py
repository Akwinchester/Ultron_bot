import telebot
from config import BOT_TOKEN
from models.user import add_user

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')


@bot.message_handler(commands=['start'])
def update(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}')
    add_user(message.from_user.first_name, message.chat.id)


if __name__ == '__main__':
    bot.infinity_polling(none_stop=True)