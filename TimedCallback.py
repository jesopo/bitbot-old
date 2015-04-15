

class Timer(object):
    def __init__(self, delay, callback, *args, **kwargs):
        self.delay = delay
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        
        self.last_called = 0
        set_last_called()
    
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
        return self.last_called+delay
    
    def call(self):
        self.set_last_called()
        self.callback(self, *self.args, **self.kwargs)