from models.models import Entry, session_scope
from data_structares import Row
from models.activity import get_related_activity_ids


@session_scope
def add_row(session, data_row: Row):
    new_row = Entry(date_added=data_row.date_added, activity_id=data_row.activity_id,
                    amount=data_row.amount, description=data_row.description)
    session.add(new_row)


@session_scope
def get_entries_for_activity_ids(session, activity_id):
    activity_ids = get_related_activity_ids(activity_id)
    entries = session.query(Entry).filter(Entry.activity_id.in_(activity_ids)).all()
    return entries
