from models.models import Activity, User, session_scope
from models.user import get_user_id
from sqlalchemy.exc import SQLAlchemyError


@session_scope
def formation_list_activity(session, user_id, status=None):
    if user_id is not None and status is not None:
        activity = session.query(Activity).filter_by(user_id=user_id, status=status).all()
    else:
        activity = session.query(Activity).filter_by(user_id=user_id).all()
    return [(act.name, act.id) for act in activity]


@session_scope
def add_activity(session, chat_id, name_activity):
    user_id = get_user_id(chat_id)
    new_activity = Activity(name=name_activity, user_id=user_id)
    session.add(new_activity)


@session_scope
def create_activity_for_template(session, activity_id, user_id):
    template_activity = session.query(Activity).get(activity_id)
    if not template_activity:
        raise ValueError(f"Activity with id {activity_id} not found")
    new_activity = Activity(name=f"{template_activity.name}", user_id=user_id)
    new_activity.related_activities.append(template_activity)
    template_activity.related_activities.append(new_activity)
    session.add(new_activity)


@session_scope
def get_name_activity(session, activity_id):
    return session.query(Activity).filter_by(id=activity_id).first().name


@session_scope
def delete_activity(session, activity_id):
    activity = session.query(Activity).get(activity_id)
    if activity:
        session.delete(activity)


@session_scope
def update_notification_text(session, activity_id, notification_text):
    activity = session.query(Activity).get(activity_id)
    if activity:
        activity.notification_text = notification_text
    else:
        print("Активность с указанным идентификатором не найдена.")


@session_scope
def toggle_friend_in_recipient(session, friend_id, activity_id):
    activity = session.query(Activity).get(activity_id)
    user = session.query(User).get(friend_id)

    if activity and user:
        if user in activity.users:
            activity.users.remove(user)
        else:
            activity.users.append(user)
    else:
        print("Активность или пользователь с указанным идентификатором не найдены.")



@session_scope
def remove_address(session, friend_id, activity_id):
    activity = session.query(Activity).get(activity_id)
    user = session.query(User).get(friend_id)
    if activity and user:
        if user in activity.users:
            activity.users.remove(user)
        else:
            print("Пользователь не связан с указанной активностью.")
    else:
        print("Активность или пользователь с указанным идентификатором не найдены.")



#Формирует список пользователей с которомы связана аткивность через таблицу user_activity
@session_scope
def formation_list_adresses(session, activity_id):
    activity = session.query(Activity).get(activity_id)
    if activity:
        adresses = activity.users
        list_adresses = []
        for ad in adresses:
            list_adresses.append(ad.as_dict())
        return list_adresses
    else:
        print("Активность не найдена.")


@session_scope
def change_status_activity(session, activity_id):
    activity = session.query(Activity).get(activity_id)
    activity.status = not activity.status


@session_scope
def get_related_activity_ids(session, activity_id):
    activity = session.query(Activity).get(activity_id)
    if not activity:
        return []
    related_ids = [a.id for a in activity.related_activities]
    related_ids.append(activity_id)
    return related_ids

# Функции, которые не работают напрямую с БД, остаются без изменений.
def formation_message_list_adresses(list_adresess:list):
    list_name_adresess = [ad['name'] for ad in list_adresess]
    str_list_name_adresess = '\n'.join(list_name_adresess)
    return f"Получатели:\n{str_list_name_adresess}"


def formation_list_chat_id(activity_id):
    list_adresess = formation_list_adresses(activity_id)
    return [ad.chat_id for ad in list_adresess]

@session_scope
def get_notification_text(session, activity_id):
    activity = session.get(Activity, activity_id)
    if activity.notification_text and activity.notification_text != '':
        return activity.notification_text
    else:
        return '-'
