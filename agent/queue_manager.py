import queue

class QueueManager:
    def __init__(self):
        self._queue = queue.Queue()

    def put_objective(self, objective):
        self._queue.put(objective)

    def get_objective(self):
        return self._queue.get()

    def is_empty(self):
        return self._queue.empty()
