from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from config import *
from datetime import date


# Создание подключения к базе данных
engine = create_engine(f'mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')



# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()



# Определение базовой модели
Base = declarative_base()

# Определение промежуточной таблицы для связи между таблицами "users" и "groups"
user_activity_table = Table('user_activity', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id', ondelete='CASCADE')),
    Column('activity_id', Integer, ForeignKey('activity.id', ondelete='CASCADE'))
)

# Определение класса-модели для таблицы
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    chat_id = Column(Integer)
    activities = relationship("Activity", secondary=user_activity_table, back_populates="users", cascade='all, delete')



class Activity(Base):
    __tablename__ = 'activity'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    user_id = Column(Integer, ForeignKey('user.id',ondelete='CASCADE'))
    users = relationship("User", secondary=user_activity_table, back_populates="activities")  # Связь "многие ко многим"



class Entry(Base):
    __tablename__ = 'entry'

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activity.id'))
    amount = Column(Integer)
    description = Column(String(300))
    date_added = Column(Date, default=date.today())
    text_notification = Column(String(300))




# # Создание таблиц
# Base.metadata.create_all(engine)