import glob, imp, inspect, os
import Utils

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
    
    def kwargs(self):
        return self._kwargs
    
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
    def __contains__(self, key):
        return key in self._kwargs
    def get(self, key, default=None):
        return self._kwargs.get(key, default)

class EventReturn(object):
    def __init__(self, path):
        self.returns = []
    
    def get(self, index=0):
        if len(self.returns) >= index+1:
            return self.returns[index]
        return None, None
    def get_all(self):
        for returned in self.returns:
            yield returned
    
    def add(self, returned):
        self.returns.append(returned)

class EventHook(object):
    def __init__(self, name=None, parent=None):
        self.name = name
        self.parent = parent
        
        self.path = []
        if parent:
            self.path = parent.path[:]
        if name:
            self.path.append(name)
        
        self._children = {}
        self._hooks = []
        self._callback_handler = None
    
    def __contains__(self, key):
        return key.lower() in self._children
    def __getitem__(self, key):
        return self.get_child(key)
    
    def get_child(self, name):
        name = str(name).lower()
        if not name in self._children:
            self._children[name] = EventHook(name, self)
            if not name.startswith("_"):
                self.on("_new_child").call(name=name, child=self._children[name])
        return self._children[name]
    def get_children(self):
        children = {}
        for child in self._children:
            if not child.startswith("_"):
                children[child] = self._children[child]
        return children
    
    def get_hooks(self):
        return self._hooks
    
    def make_event(self, original_path=None, **kwargs):
        return Event(self.path, original_path, **kwargs)
    
    def set_callback_handler(self, function):
        self._callback_handler = function
    def get_callback_handler(self):
        return self._callback_handler
    def default_callback_handler(self):
        self._callback_handler = None
    
    def on(self, *path):
        if len(path):
            hook = self
            for name in path:
                hook = hook.get_child(name)
            return hook
        return self
    
    def hook(self, function, receive_children=False, **options):
        self._hooks.append([function, receive_children, options])
        return self
    def get_hooks(self):
        return self._hooks
    
    def call(self, original_path=None, returns=None, **kwargs):
        event = self.make_event(original_path, **kwargs)
        returns = returns or EventReturn(original_path or self.path)
        for function, receive_children, options in self.get_hooks():
            if original_path and not receive_children:
                continue
            if event.stopped_propagation():
                break
            if not self._callback_handler:
                returned = function(event)
            else:
                returned = self._callback_handler(function, options, event)
            if not returned == None:
                returns.add(returned)
        original_path = original_path or self.path
        if self.parent and not event.stopped_escalation():
            self.parent.call(original_path, **kwargs)
        return returns

class ModuleManager(object):
    def __init__(self, bot, directory="modules"):
        self.bot = bot
        self.directory = os.path.join(Utils.current_directory, directory)
        self.modules = []
        self.events = EventHook()
        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)
    
    def list_modules(self):
        return sorted(glob.glob(os.path.join(self.directory, "*.py")))
        
    def load_module(self, filename):
        name = os.path.basename(filename)[:-3]
        with open(filename) as file_object:
            while True:
                line = file_object.readline().strip()
                if line and line.startswith("#--"):
                    if line == "#--ignore":
                        return None
                    # moar hashflags here
                else:
                    break
        module = imp.load_source("module_%s" % name, filename)
        assert hasattr(module, "Module"), """module '%s' doesn't have a
            'module' class."""
        assert inspect.isclass(module.Module), """module '%s' has something
            called 'module' but it's not a class."""
        module_object = module.Module(self.bot)
        if not hasattr(module_object, "_name"):
            module_object._name = name[0].upper() + name[1:]
        # I feel kinda bad for having to truncate module names :<
        module_object._name = module_object._name[:32]
        return module_object
    
    def load_modules(self):
        for filename in self.list_modules():
            module = self.load_module(filename)
            self.modules.append(module)