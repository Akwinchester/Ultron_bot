from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Table, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from config import *
from datetime import date
from functools import wraps
from logger import logger

# Создание подключения к базе данных
engine = create_engine(f'mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')


# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()


# Определение базовой модели
Base = declarative_base()


# Определение промежуточной таблицы для связи пользователя и активностей. Кто получает уведомления
user_activity_table = Table('user_activity', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id', ondelete='CASCADE')),
    Column('activity_id', Integer, ForeignKey('activity.id', ondelete='CASCADE')),
    Column('address', Boolean, default=False),
    Column('add_entery', Boolean, default=False)
)


#Связь пользователь-пользователь список друзей
user_friend_table = Table('user_friend', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    Column('friend_id', Integer, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
)


activity_activity_table = Table('activity_activity',Base.metadata,
                         Column('activity_one_id', Integer,  ForeignKey('activity.id', ondelete='CASCADE'), primary_key=True),
                         Column('activity_two_id', Integer, ForeignKey('activity.id', ondelete='CASCADE'), primary_key=True),
                         )


# Определение класса-модели для таблицы
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    chat_id = Column(String(50))
    activities = relationship("Activity", secondary=user_activity_table, back_populates="users", cascade='all, delete')
    nick  = Column(String(50), default='')
    friends = relationship("User",
                           secondary=user_friend_table,
                           primaryjoin=id == user_friend_table.c.user_id,
                           secondaryjoin=id == user_friend_table.c.friend_id,
                           backref="user_friends")

    def add_friend(self, friend):
        if friend not in self.friends:
            self.friends.append(friend)
            friend.friends.append(self)

    def remove_friend(self, friend):

        if friend in self.friends:
            for activity in friend.activities:
                activity.users.remove(friend)
            friend.friends.remove(self)
            self.friends.remove(friend)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Activity(Base):
    __tablename__ = 'activity'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    notification_text = Column(String(500), default='')
    status = Column(Boolean, default=True)
    users = relationship("User", secondary=user_activity_table, back_populates="activities")
    related_activities = relationship('Activity',
                                       secondary=activity_activity_table,
                                       primaryjoin=id == activity_activity_table.c.activity_one_id,
                                       secondaryjoin=id == activity_activity_table.c.activity_two_id,
                                       lazy='dynamic')


class Entry(Base):
    __tablename__ = 'entry'

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activity.id', ondelete='CASCADE'))
    amount = Column(Integer)
    description = Column(String(300), default='')
    date_added = Column(Date, default=date.today())



def session_scope(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()  # Создаем новую сессию
        try:
            result = func(session, *args, **kwargs)  # Передаем сессию как первый аргумент вашей функции
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    return wrapper