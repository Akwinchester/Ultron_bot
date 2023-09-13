from models.models import User, session
from logger import logger

#Запись в БД
def create_user(real_name, chat_id, nick):
    if not check_user_exists(chat_id):
        new_user = User(name=real_name, chat_id=chat_id, nick = nick, username='', password='')
        session.add(new_user)
        session.commit()
        session.close()


#Проеверка наличия пользователя с таким chat_id
def check_user_exists(chat_id):
    user = session.query(User).filter_by(chat_id=chat_id).one_or_none()
    return user is not None


#Получение user_id по chat_id
def get_user_id(chat_id):
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        user_id = user.id
        return user_id
    else:
        print('chat_id нет в базе')
        return 1

def get_user_name(user_id):
    user_name = session.get(User, user_id).name
    return user_name


def get_list_friend(user_id):
    user = session.get(User, user_id)  # Получение объекта пользователя по ID

    if user:
        friends = user.friends
        return friends
    else:
        logger.info('Пользователь не найден')


def add_friend(user_id, nick):
    user = session.get(User, user_id)
    friend = session.query(User).filter(User.nick==nick).first()

    if user and friend and not friend in user.friends:
        user.add_friend(friend)
        session.commit()
        session.close()
        return True
    session.close()
    return False


def check_user_name_bd(username):
    user = session.query(User).filter(User.username==username).first()
    return user


def update_user(user_name, real_name, chat_id, nick):
    if not check_user_exists(chat_id):
        user = session.query(User).filter(User.username == user_name).first()
        user.chat_id = chat_id
        user.nick = nick
        user.name = real_name
        session.commit()
        session.close()
    else:
        logger.info('chat_id уже есть в базе')