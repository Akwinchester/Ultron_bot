import telebot
from config import BOT_TOKEN


message_id_for_edit = {}
user_row = {}

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')
