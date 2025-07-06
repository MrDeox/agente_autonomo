import queue

class QueueManager:
    def __init__(self):
        self._queue = queue.Queue()

    def put_objective(self, objective):
        self._queue.put(objective)

    def get_objective(self, timeout=None):
        try:
            return self._queue.get(block=True, timeout=timeout)
        except queue.Empty:
            return None

    def is_empty(self):
        return self._queue.empty()
