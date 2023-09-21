from models.models import User, session_scope
from logger import logger
from sqlalchemy.orm import joinedload


@session_scope
def create_user(session, real_name, chat_id, nick):
    if not check_user_exists(chat_id):
        new_user = User(name=real_name, chat_id=chat_id, nick=nick, username='', password='')
        session.add(new_user)


@session_scope
def check_user_exists(session, chat_id):
    user = session.query(User).filter_by(chat_id=chat_id).one_or_none()
    return True is not None


@session_scope
def get_user_id(session, chat_id):
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        return user.id
    else:
        logger.info('chat_id нет в базе')
        return 1


@session_scope
def get_user_name(session, user_id):
    return session.get(User, user_id).name


@session_scope
def get_list_friend(session, user_id):
    user = session.get(User, user_id)
    if user:
        friends = user.friends
        friens_list = []
        for f in friends:
            friens_list.append(f.as_dict())
        return friens_list
    else:
        return None


@session_scope
def add_friend(session, user_id, nick):
    user = session.get(User, user_id)
    friend = session.query(User).filter(User.nick == nick).first()

    if user and friend and friend not in user.friends:
        user.add_friend(friend)
        return True
    return False


@session_scope
def remove_friend(session, user_id, friend_id):
    user = session.get(User, user_id)
    friend = session.get(User, friend_id)
    logger.debug(user_id)
    logger.debug(friend_id)

    if user and friend:
        user.remove_friend(friend)
        return True
    return False

@session_scope
def check_user_name_bd(session, username):
    user = session.query(User).filter(User.username == username).first()
    user_data = {'user_name':user.username, 'password':user.password}
    return user_data


@session_scope
def update_user(session, user_name, real_name, chat_id, nick):
    if check_user_exists(chat_id):
        user = session.query(User).filter(User.username == user_name).first()
        user.chat_id = chat_id
        user.nick = nick
        user.name = real_name
    else:

        logger.info('chat_id уже есть в базе')
