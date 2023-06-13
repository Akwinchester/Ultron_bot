from models.models import User, session


def create_user(real_name, chat_id):
    if not check_user_exists(chat_id):
        new_user = User(name=real_name, chat_id=chat_id)
        session.add(new_user)
        session.commit()
        session.close()


def check_user_exists(chat_id):
    user = session.query(User).filter_by(chat_id=chat_id).one_or_none()
    return user is not None


def get_user_id(chat_id):
    user_id = session.query(User).filter_by(chat_id=chat_id).first().id
    return user_id
