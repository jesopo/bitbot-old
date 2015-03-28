import glob, imp, inspect, os

current_directory = os.path.dirname(os.path.abspath(__file__))

class Event(object):
    def __init__(self, path, original_path=None, **kwargs):
        self.path = path
        self.name = path[-1]
        self.original_path = original_path
        self._kwargs = kwargs
        self._eaten = False
    
    def eat(self):
        self._eaten = True
    def is_eaten(self):
        return self._eaten
    
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
    
    def on(self, name):
        if not name in self.children:
            self.children[name] = self.__class__(name, self)
        return self.children[name]
    
    def hook(self, function):
        self.hooks.add(function)
    
    def call(self, original_path=None, **kwargs):
        event = Event(self.path, original_path, **kwargs)
        for function in self.hooks:
            if event.is_eaten():
                return
            function(event)
        if self.parent and self.parent.parent:
            self.parent.call(original_path, **kwargs)
    
    def from_path(self, *path):
        if len(path):
            hook = self.on(path[0])
            for step in path:
                hook = hook.on(step)
            return hook

class ModuleManager(object):
    def __init__(self, directory="modules"):
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
        assert hasattr(module, "module"), """module '%s' doesn't have a
            'module' class."""
        assert inspect.isclass(module.module), """module '%s' has something
            called 'module' but it's not a class."""
        module.module(self.events)
        return module
    
    def load_modules(self):
        for filename in self.list_modules():
            module = self.load_module(filename)
            self.modules.append(module)