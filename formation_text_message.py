from config import MESSAGE_TEXT
from models.activity import get_name_activity, formation_list_activity
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
Дата добавления: <b>{row.date_added}</b>

Активность: <b>{get_name_activity(row.activity_id)}</b>

Количество: <b>{row.amount}</b>

Описание: <b>{row.description}</b>'''

     elif row.amount == 0 and row.description != '-':
          return f'''
Дата добавления: <b>{row.date_added}</b>

Активность: <b>{get_name_activity(row.activity_id)}</b>

Описание: <b>{row.description}</b>'''

     elif row.amount != 0 and row.description == '-':
          return f'''
Дата добавления: <b>{row.date_added}</b>

Активность: <b>{get_name_activity(row.activity_id)}</b>

Количество: <b>{row.amount}</b>'''

     elif row.amount == 0 and row.description == '-':
          return f'''
Дата добавления: <b>{row.date_added}</b>

Активность: <b>{get_name_activity(row.activity_id)}</b>'''


def list_activity_True(user_id):
     list_str = ''
     list_object = formation_list_activity(user_id)
     for act in list_object:
          list_str+= act[0] + '\n'

     return f'Здесь ты можешь настраивать список активностей, в которые будешь добавлять записи\n\nАктивные активности:\n{list_str}'