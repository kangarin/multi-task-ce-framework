# from abc import ABC, abstractmethod, abstractclassmethod, abstractstaticmethod, abstractproperty

# class Task_v2(ABC):
#     @abstractclassmethod
#     def task_type(cls) -> str:
#         pass

#     @abstractclassmethod
#     def task_description(cls) -> str:
#         pass

#     @abstractmethod
#     def __init__(self, 
#                  data: object, 
#                  seq_id: int, 
#                  source_id: str, 
#                  importance: float,
#                  urgency: float,
#                  importance_urgency_ratio: float,
#                  deadline: float,
#                  start_time: float,
#                  initial_priority: int
#                  ) -> None:
#         self._data = data
#         self._seq_id = seq_id
#         self._source_id = source_id
#         self._importance = importance
#         self._urgency = urgency
#         self._importance_urgency_ratio = importance_urgency_ratio
#         self._deadline = deadline
#         self._start_time = start_time
#         self._priority = initial_priority

#     @abstractmethod
#     def get_data(self) -> list:
#         pass

#     @abstractmethod
#     def get_seq_id(self) -> str:
#         pass

#     @abstractmethod
#     def get_source_id(self) -> str:
#         pass

#     @abstractmethod
#     def get_priority(self) -> int:
#         pass

#     @abstractmethod
#     def set_priority(self, priority: int):
#         pass

#     @abstractmethod
#     def get_importance(self) -> float:
#         pass

#     @abstractmethod
#     def set_importance(self, importance: float):
#         pass

#     @abstractmethod
#     def get_urgency(self) -> float:
#         pass

#     @abstractmethod
#     def set_urgency(self, urgency: float):
#         pass

#     @abstractmethod
#     def get_importance_urgency_ratio(self) -> float:
#         pass

#     @abstractmethod
#     def get_deadline(self) -> float:
#         pass

#     @abstractmethod
#     def get_start_time(self) -> float:
#         pass

#     @abstractmethod
#     def serialize(self) -> dict:
#         pass

#     @abstractstaticmethod
#     def deserialize(data: dict):
#         pass


from framework.task_v2 import Task_v2

class Task_v2_Impl(Task_v2):
    @classmethod
    def task_type(cls) -> str:
        return 'video'

    @classmethod
    def task_description(cls) -> str:
        return 'Video task'

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

    def get_data(self) -> list:
        return self._data

    def get_seq_id(self) -> str:
        return self._seq_id

    def get_source_id(self) -> str:
        return self._source_id

    def get_priority(self) -> int:
        return self._priority

    def set_priority(self, priority: int):
        self._priority = priority

    def get_importance(self) -> float:
        return self._importance

    def set_importance(self, importance: float):
        self._importance = importance

    def get_urgency(self) -> float:
        return self._urgency

    def set_urgency(self, urgency: float):
        self._urgency = urgency

    def get_importance_urgency_ratio(self) -> float:
        return self._importance_urgency_ratio

    def get_deadline(self) -> float:
        return self._deadline

    def get_start_time(self) -> float:
        return self._start_time

    def serialize(self) -> dict:
        return {
            'data': self._data,
            'seq_id': self._seq_id,
            'source_id': self._source_id,
            'importance': self._importance,
            'urgency': self._urgency,
            'importance_urgency_ratio': self._importance_urgency_ratio,
            'deadline': self._deadline,
            'start_time': self._start_time,
            'priority': self._priority
        }
    
    @staticmethod
    def deserialize(data: dict):
        return Task_v2_Impl(
            data=data['data'],
            seq_id=data['seq_id'],
            source_id=data['source_id'],
            importance=data['importance'],
            urgency=data['urgency'],
            importance_urgency_ratio=data['importance_urgency_ratio'],
            deadline=data['deadline'],
            start_time=data['start_time'],
            priority=data['priority']
        )
    
    def __lt__(self, other):
        return self.get_priority() > other.get_priority()