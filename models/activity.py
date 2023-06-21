from models.models import Activity, User, session
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


#Удаление категории
def delete_activity(activity_id):
    try:
        activity = session.query(Activity).get(activity_id)

        if activity:
            session.delete(activity)
            session.commit()

    except SQLAlchemyError as e:
        print("Ошибка при удалении записи:", str(e))
        session.rollback()

    finally:
        session.close()


#обновление\добавление текста для уведомления
def update_notification_text(activity_id, notification_text):
    activity = session.query(Activity).get(activity_id)
    if activity:
        activity.notification_text = notification_text
        session.commit()
        session.close()
    else:
        print("Активность с указанным идентификатором не найдена.")


def add_address(friend_id, activity_id):
    try:
        activity = session.query(Activity).get(activity_id)
        user = session.get(User, friend_id)
        if activity is None or user is None:
            return False  # Возвращаем False, если активность или пользователь не найдены

        # Добавляем связь между активностью и пользователем
        activity.users.append(user)
        session.commit()
        return True  # Возвращаем True, если связь успешно добавлена

    except Exception as e:
        print(f"Error adding address: {e}")
        session.rollback()
        return False  # Возвращаем False в случае ошибки

    finally:
        session.close()


def formation_list_adresses(activity_id):
    activity = session.query(Activity).get(activity_id)

    if activity:
        # Получение списка пользователей связанных с активностью
        users = activity.users
        return users
    else:
        print("Активность не найдена.")


def formation_message_list_adresses(list_adresess:list):
    list_name_adresess = []
    for ad in list_adresess:
        list_name_adresess.append(ad.name)

    str_list_name_adresess = '\n'.join(list_name_adresess)
    message_text = f'''
Получатели:
{str_list_name_adresess}'''
    return message_text


def formation_list_chat_id(activity_id):
    list_adresess = formation_list_adresses(activity_id)
    list_chat_id = []
    for ad in list_adresess:
        list_chat_id.append(ad.chat_id)
    return list_chat_id


def get_notification_text(activity_id):
    activity = session.get(Activity, activity_id)
    if activity.notification_text  and activity.notification_text != '':
        return activity.notification_text
    else:
        return False