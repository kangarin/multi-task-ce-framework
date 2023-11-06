from abc import ABC, abstractclassmethod, abstractstaticmethod, abstractmethod
from framework.task import Task

class Generator(ABC):
    @abstractclassmethod
    def generator_type(cls) -> str:
        pass

    @abstractclassmethod
    def generator_description(cls) -> str:
        pass

    @abstractmethod
    def __init__(self, data_source: object, id: str, mq_topic: str, 
                 priority: int, tuned_parameters: dict) -> None:
        self._data_source = data_source
        self._id = id
        self._mq_topic = mq_topic
        self._priority = priority
        self._tuned_parameters = tuned_parameters

    @abstractmethod
    def get_data_source(self) -> object:
        pass

    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def get_mq_topic(self) -> str:
        pass

    @abstractmethod
    def get_priority(self) -> int:
        pass

    @abstractmethod
    def set_priority(self, priority: int):
        pass

    @abstractmethod
    def get_tuned_parameters(self) -> dict:
        pass

    @abstractmethod
    def set_tuned_parameters(self, tuned_parameters: dict):
        pass

    @abstractmethod
    def send_task_to_mq(self, task: Task):
        pass

    '''Should be implemented as a while loop that yields tasks'''
    @abstractmethod
    def run(self):
        pass
