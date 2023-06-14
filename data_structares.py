from dataclasses import dataclass
from datetime import date


#Объект для хранения данных записи
@dataclass
class Row:
    date_added: date
    activity_id: int
    amount: int
    description: str


#Фабрика собирающая объект класса Row
class RowFactory:
    def __init__(self):
        self.data = {}

    def set_date_added(self, date_added: date):
        self.data['date_added'] = date_added

    def set_activity_id(self, activity_id: int):
        self.data['activity_id'] = activity_id

    def set_amount(self, amount: int):
        self.data['amount'] = amount

    def set_description(self, description: str):
        self.data['description'] = description

    def create_row(self) -> Row:
        return Row(**self.data)
