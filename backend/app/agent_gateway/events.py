from .models import RuntimeEvent


class EventCursor:
    def __init__(self, last_event_id: str | None = None) -> None:
        self.last_event_id = last_event_id

    def accept(self, event: RuntimeEvent) -> bool:
        if not event.event_id or event.event_id == self.last_event_id:
            return bool(event.event_id) and event.event_id != self.last_event_id
        self.last_event_id = event.event_id
        return True
