from dataclasses import dataclass
from typing import List, Dict, Union, Optional

class EventDataContainer:
    __slots__ = "events_dict"

    def __init__(self):
        self.events_dict: Dict[str, Dict[int, float]] = {}

    def update_event(self, events: Dict[str, Dict[int, float]]) -> None:
        for eventType, eventDict in events.items():
            if eventType not in self.events_dict:
                self.events_dict[eventType] = eventDict
            else:
                for eventEnum, eventStatus in eventDict.items():  # додали .items()
                    self.events_dict[eventType][eventEnum] = eventStatus

    def get_event(self, tag: str) -> Dict[int, float]:
        return self.events_dict.get(tag, {})

    def get_all_events(self) -> Dict[str, Dict[int, float]]:
        return self.events_dict