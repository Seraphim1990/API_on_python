from dataclasses import dataclass
from typing import List, Dict, Union

@dataclass
class HashedValue:
    tag: str
    timestamp: int
    value: float

class ValuesDataContainer:
    __slots__ = "values_dict"

    def __init__(self):
        self.values_dict = {}

    def update_values(self, values: list):
        for item in values:
            self.values_dict[item.tag] = item

    def get_value(self, tag: str) -> Union[HashedValue, None]:
        return self.values_dict.get(tag)

    def get_many_values(self, tags: List[str]) -> Dict[str, HashedValue]:
        result = {}
        for tag in tags:
            if tag in self.values_dict:
                result[tag] = self.values_dict[tag]
        return result

    def get_all_values(self) -> list:
        result = []
        for key, value in self.values_dict.items():
            result.append(value)
        return result