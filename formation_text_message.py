from config import MESSAGE_TEXT
from models.activity import get_name_activity


def select_activity(activity_id):
     return f'''Выбранная активность: <b>{get_name_activity(activity_id)}</b>
Вернись назад с помощью кнопки: <b>Список активностей</b>

Продолжи добавление записи с помощью кнопки: <b>Продолжить</b>

Перейди в режим настройки уведомлений с помощью кнопки: <b>Уведомления</b>
'''


def setting_notification(activity_id):
     return f'''Настройка текста уведомления и получателей уведомления для активности: <b>{get_name_activity(activity_id)}</b>'''