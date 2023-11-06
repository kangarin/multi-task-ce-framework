from abc import ABC, abstractmethod, abstractclassmethod, abstractstaticmethod, abstractproperty

class Task(ABC):
    @abstractclassmethod
    def task_type(cls) -> str:
        pass

    @abstractclassmethod
    def task_description(cls) -> str:
        pass

    @abstractmethod
    def __init__(self, data: object, seq_id: int, source_id: str, priority: int) -> None:
        self._data = data
        self._seq_id = seq_id
        self._source_id = source_id
        self._priority = priority

    @abstractmethod
    def get_data(self) -> list:
        pass

    @abstractmethod
    def get_seq_id(self) -> str:
        pass

    @abstractmethod
    def get_source_id(self) -> str:
        pass

    @abstractmethod
    def get_priority(self) -> int:
        pass

    @abstractmethod
    def set_priority(self, priority: int):
        pass

    @abstractmethod
    def serialize(self) -> dict:
        pass

    @abstractstaticmethod
    def deserialize(data: dict):
        pass

