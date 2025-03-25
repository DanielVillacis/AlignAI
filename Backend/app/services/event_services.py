from domain.models import db
from domain.entities import Event
from datetime import datetime, timedelta

class EventService:
    @staticmethod
    def create_event(data):
        # parse the datetime string and store it as UTC
        event_date = datetime.fromisoformat(data['event_date'].replace('Z', '+00:00'))
        new_event = Event(
            title=data['title'],
            description=data.get('description', ''),
            event_date=event_date,
            client_id=data.get('client_id'),
            is_scan=data.get('is_scan', False)
        )
        db.session.add(new_event)
        db.session.commit()
        return new_event

    @staticmethod
    def get_events_by_date(date_str):
        target_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        start_of_day = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return Event.query.filter(
            Event.event_date >= start_of_day,
            Event.event_date < end_of_day
        ).all()

    @staticmethod
    def get_all_events():
        return Event.query.all()

    @staticmethod
    def get_event_by_id(id):
        return Event.query.get_or_404(id)

    @staticmethod
    def update_event(event, data):
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'event_date' in data:
            event.event_date = datetime.fromisoformat(data['event_date'])
        if 'client_id' in data:
            event.client_id = data['client_id']
        if 'is_scan' in data:
            event.is_scan = data['is_scan']
        
        db.session.commit()
        return event

    @staticmethod
    def delete_event(event):
        db.session.delete(event)
        db.session.commit()