from models.models import Activity, session
from models.user import get_user_id


#Список для формирования кнопок выбора активности [(название_активности, id_активности),]
def formation_list_activity(chat_id):
    user_id = get_user_id(chat_id)
    activity = session.query(Activity).filter_by(user_id=user_id).all()
    session.close()
    list_activity = []
    for act in activity:
        list_activity.append((act.name, act.id))
    return list_activity


#Запись в БД
def add_activity(chat_id, name_activity):
    user_id = get_user_id(chat_id)
    new_activity = Activity(name=name_activity, user_id=user_id)
    session.add(new_activity)
    session.commit()
    session.close()


#Получение названия активности по id
def get_name_activity(activity_id):
    activity_name = session.query(Activity).filter_by(id = activity_id).first().name
    session.close()
    return activity_name
