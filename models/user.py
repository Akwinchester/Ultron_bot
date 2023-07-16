from models.models import User, session

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
    user_id = session.query(User).filter_by(chat_id=chat_id).first().id
    return user_id


def get_list_friend(user_id):
    user = session.get(User, user_id)  # Получение объекта пользователя по ID

    if user:
        friends = user.friends
        return friends
    else:
        print("Пользователь не найден")


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