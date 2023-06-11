from models.models import User, session


def add_user(real_name, chat_id):
    new_user = User(name=real_name, chat_id=chat_id)
    session.add(new_user)
    session.commit()
    session.close()