from abc import ABC, abstractmethod, abstractclassmethod, abstractstaticmethod, abstractproperty

class Task_v2(ABC):
    @abstractclassmethod
    def task_type(cls) -> str:
        pass

    @abstractclassmethod
    def task_description(cls) -> str:
        pass

    @abstractmethod
    def __init__(self, 
                 data: object, 
                 seq_id: int, 
                 source_id: str, 
                 importance: float,
                 urgency: float,
                 importance_urgency_ratio: float,
                 deadline: float,
                 start_time: float,
                 priority: int
                 ) -> None:
        self._data = data
        self._seq_id = seq_id
        self._source_id = source_id
        self._importance = importance
        self._urgency = urgency
        self._importance_urgency_ratio = importance_urgency_ratio
        self._deadline = deadline
        self._start_time = start_time
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
    def get_importance(self) -> float:
        pass

    @abstractmethod
    def set_importance(self, importance: float):
        pass

    @abstractmethod
    def get_urgency(self) -> float:
        pass

    @abstractmethod
    def set_urgency(self, urgency: float):
        pass

    @abstractmethod
    def get_importance_urgency_ratio(self) -> float:
        pass

    @abstractmethod
    def get_deadline(self) -> float:
        pass

    @abstractmethod
    def get_start_time(self) -> float:
        pass

    @abstractmethod
    def serialize(self) -> dict:
        pass

    @abstractstaticmethod
    def deserialize(data: dict):
        pass

