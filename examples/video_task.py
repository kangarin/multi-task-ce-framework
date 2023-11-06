from framework.task import Task

class VideoTask(Task):
    def __init__(self, data: object, seq_id: int, source_id: str, priority: int, metadata: dict = None):
        super().__init__(data, seq_id, source_id, priority)
        self._metadata = metadata

    @classmethod
    def task_type(cls) -> str:
        return 'video'
    
    @classmethod
    def task_description(cls) -> str:
        return 'Video task'
    
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

    def get_metadata(self) -> dict:
        return self._metadata
    
    def set_metadata(self, metadata: dict):
        self._metadata = metadata

    def serialize(self) -> dict:
        return {'data': self._data, 'seq_id': self._seq_id, 'source_id': self._source_id, 'priority': self._priority, 'metadata': self._metadata}
    
    @staticmethod
    def deserialize(data: dict):
        return VideoTask(data['data'], data['seq_id'], data['source_id'], data['priority'], data['metadata'])