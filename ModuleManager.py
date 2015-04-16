import glob, imp, inspect, os

current_directory = os.path.dirname(os.path.abspath(__file__))

class Event(object):
    def __init__(self, path, original_path=None, **kwargs):
        self.path = path
        self.name = ""
        if len(path):
            self.name = path[-1]
        self.original_path = original_path
        self._kwargs = kwargs
        self._stop_propagation = False
        self._stop_escalation = False
    
    def stop_propagation(self):
        self._stop_propagation = True
    def stopped_propagation(self):
        return self._stop_propagation
    
    def stop_escalation(self):
        self._stop_escalation = True
    def stopped_escalation(self):
        return self._stop_escalation
    
    def stop(self):
        self.stop_escalation()
        self.stop_propagation()
    
    def __getitem__(self, key):
        return self._kwargs[key]

class EventHook(object):
    def __init__(self, name=None, parent=None):
        self.name = name
        self.parent = parent
        
        self.path = []
        if parent:
            path = parent.path
        if name:
            self.path.append(name)
        
        self.children = {}
        self.hooks = set([])
    
    def get_child(self, name):
        if not name in self.children:
            self.children[name] = self.__class__(name, self)
        return self.children[name]
    
    def on(self, *path):
        if len(path):
            hook = self
            for name in path:
                hook = hook.get_child(name)
            return hook
        return self
    
    def hook(self, function):
        self.hooks.add(function)
        return self
    
    def call(self, original_path=None, **kwargs):
        event = Event(self.path, original_path, **kwargs)
        for function in self.hooks:
            if event.stopped_propagation():
                break
            function(event)
        if self.parent and not event.stopped_escalation():
            self.parent.call(original_path, **kwargs)
        return self

class ModuleManager(object):
    def __init__(self, bot, directory="modules"):
        self.bot = bot
        self.directory = os.path.join(current_directory, directory)
        self.modules = []
        self.events = EventHook()
        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)
    
    def list_modules(self):
        return glob.glob("%s/*.py" % self.directory)
        
    def load_module(self, filename):
        name = "module_%s" % os.path.basename(filename)[:-3]
        with open(filename) as file_object:
            while True:
                line = file_object.readline().strip()
                if line and line.startswith("#--"):
                    if line == "#--ignore":
                        return None
                    # moar hashflags here
                else:
                    break
        module = imp.load_source(name, filename)
        assert hasattr(module, "Module"), """module '%s' doesn't have a
            'module' class."""
        assert inspect.isclass(module.Module), """module '%s' has something
            called 'module' but it's not a class."""
        module.Module(self.bot)
        return module
    
    def load_modules(self):
        for filename in self.list_modules():
            module = self.load_module(filename)
            self.modules.append(module)