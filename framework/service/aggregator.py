from abc import ABC, abstractclassmethod, abstractstaticmethod, abstractmethod
from framework.task import Task

class Aggregator(ABC):
    @abstractclassmethod
    def aggregator_type(cls) -> str:
        pass

    @abstractclassmethod
    def aggregator_description(cls) -> str:
        pass

    @abstractmethod
    def __init__(self, id: str, incoming_mq_topic: str, tuned_parameters: dict) -> None:
        self._id = id
        self._incoming_mq_topic = incoming_mq_topic
        self._tuned_parameters = tuned_parameters

    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def get_incoming_mq_topic(self) -> str:
        pass

    @abstractmethod
    def get_tuned_parameters(self) -> dict:
        pass

    @abstractmethod
    def set_tuned_parameters(self, tuned_parameters: dict):
        pass

    @abstractmethod
    def get_task_from_incoming_mq(self) -> Task:
        pass

    @abstractmethod
    def get_latest_results(self) -> list:
        pass

    '''Should be implemented as a while loop that yields tasks'''
    @abstractmethod
    def run(self):
        pass