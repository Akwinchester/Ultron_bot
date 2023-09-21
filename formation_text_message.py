from config import MESSAGE_TEXT
from models.activity import get_name_activity, formation_list_activity
from models.user import get_list_friend
from data_structares import Row


def select_activity(activity_id):
     return f'''Выбранная активность: <b>{get_name_activity(activity_id)}</b>
Вернись назад с помощью кнопки: <b>Список активностей</b>

Продолжи добавление записи с помощью кнопки: <b>Продолжить</b>

Перейди в режим настройки уведомлений с помощью кнопки: <b>Уведомления</b>
'''


def setting_notification(activity_id):
     return f'''Настройка текста уведомления и получателей уведомления для активности: <b>{get_name_activity(activity_id)}</b>'''


def tg_entry_text(row:Row):
     if row.amount != 0 and row.description != '-':
          return f'''
Пользователь: <b>{row.user_name}</b>

Дата добавления: <b>{row.date_added}</b>

Активность: <b>{get_name_activity(row.activity_id)}</b>

Количество: <b>{row.amount}</b>

Описание: <b>{row.description}</b>'''

     elif row.amount == 0 and row.description != '-':
          return f'''
Пользователь: <b>{row.user_name}</b>

Дата добавления: <b>{row.date_added}</b>

Активность: <b>{get_name_activity(row.activity_id)}</b>

Описание: <b>{row.description}</b>'''

     elif row.amount != 0 and row.description == '-':
          return f'''
Пользователь: <b>{row.user_name}</b>

Дата добавления: <b>{row.date_added}</b>

Активность: <b>{get_name_activity(row.activity_id)}</b>

Количество: <b>{row.amount}</b>'''

     elif row.amount == 0 and row.description == '-':
          return f'''
Пользователь: <b>{row.user_name}</b>

Дата добавления: <b>{row.date_added}</b>

Активность: <b>{get_name_activity(row.activity_id)}</b>'''


def list_activity_True(user_id):
     list_str = ''
     list_object = formation_list_activity(user_id)
     for act in list_object:
          list_str+= act[0] + '\n'

     return f'''Здесь ты можешь настраивать список активностей, в которые будешь добавлять записи.\n
<b>Добавить новую активность:</b> просто отправь ее название следующим сообщением\n
<b>Синхронизироваться с активностью друга:</b> нажми на имя друга и выбери активность из списка доступных\n
<b>Мои ахивированные активности:</b> мои активности\n
\n\n<b>Активные активности:</b>\n{list_str}'''


def list_name_friends(user_id):
     list_friends = get_list_friend(user_id)
     text_list_name_friend = '<b>Ваши друзья:</b>\n'
     for f in list_friends:
          text_list_name_friend += '- ' + f['name'] + '\n'
     return text_list_name_friend