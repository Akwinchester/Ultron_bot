from models.models import Entry, session
from data_structares import Row, RowFactory


#Запись в БД
def add_row(data_row:Row):
    new_row = Entry(date_added=data_row.date_added, activity_id=data_row.activity_id,
                    amount=data_row.amount, description=data_row.description)
    session.add(new_row)
    session.commit()
    session.close()