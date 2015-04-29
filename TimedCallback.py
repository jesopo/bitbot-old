import time

class Timer(object):
    def __init__(self, callback, delay, *args, **kwargs):
        self._destroyed = False
        
        self.callback = callback
        self.delay = delay
        self.args = args
        self.kwargs = kwargs
        
        self.last_called = 0
        self.set_last_called()
    
    def set_last_called(self):
        self.last_called = time.time()
    
    def time_until(self):
        if not self.last_called:
            return delay
        to_wait = time.time()-self.due_at()
        if to_wait < 0:
            return 0
        return to_wait
    
    def due_at(self):
        return self.last_called+self.delay
    def due(self):
        return time.time() >= self.last_called+self.delay
    
    def call(self):
        self.set_last_called()
        self.callback(self, *self.args, **self.kwargs)
    
    def destroy(self):
        self._destroyed = True
    def is_destroyed(self):
        return self._destroyed