from abc import ABC, abstractclassmethod, abstractstaticmethod, abstractmethod
from framework.task import Task

class Distributor(ABC):
    @abstractclassmethod
    def distributor_type(cls) -> str:
        pass

    @abstractclassmethod
    def distributor_description(cls) -> str:
        pass

    @abstractmethod
    def __init__(self, id: str, incoming_mq_topic: str) -> None:
        self._id = id
        self._incoming_mq_topic = incoming_mq_topic

    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def get_incoming_mq_topic(self) -> str:
        pass

    @abstractmethod
    def get_task_from_incoming_mq(self) -> Task:
        pass

    @abstractmethod
    def distribute_task_to_outgoing_mq_list(self, task: Task):
        pass

    '''Should be implemented as a while loop that yields tasks'''
    @abstractmethod
    def run(self):
        pass