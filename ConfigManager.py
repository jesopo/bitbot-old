import glob, os
import yaml

current_directory = os.path.dirname(os.path.abspath(__file__))

class ConfigObject(object):
    underlying = object
    def __init__(self, config, parent):
        self.initialised = False
        
        self.parent = parent
        self.filename = None
        self.underlying.__init__(self)
        self.make(config)
        self.overwrites()
        self.should_commit = True
        self.initialised = True
    
    def __enter__(self):
        self.should_commit = False
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.should_commit = True
        self.commit()
    
    def commit(self, config=None, filename=None):
        if self.initialised and self.should_commit:
            self.parent.commit(self, self.filename)
    
    def overwrites(self):
        pass
    
    def make(self, config):
        pass
    def unmake(self):
        pass
    
    def wrap_object(self, obj):
        if type(obj) == dict:
            config = ConfigDictionary(obj, self)
            return config
        elif type(obj) == list:
            config = ConfigList(obj, self)
            return config
        return obj
    
    def commit_call(self, function):
        def call(*args, **kwargs):
            val = function(*args, **kwargs)
            self.commit(self)
            return val
        setattr(self, function.__name__, call)
    
    def __setitem__(self, key, value):
        self.underlying.__setitem__(self, key, self.wrap_object(value))
        self.commit()
    def __delitem__(self, key):
        self.underlying.__delitem__(self, key)
        self.commit()

class ConfigDictionary(ConfigObject, dict):
    underlying = dict
    def overwrites(self):
        self.commit_call(self.clear)
        self.commit_call(self.pop)
        self.commit_call(self.popitem)
    
    def update(self, other=None, **kwargs):
        other = other or kwargs
        for key in other:
            other[key] = self.wrap_object(other[key])
        self.underlying.update(self, other)
    
    def make(self, config):
        for key in config:
            self[key] = config[key]
    def unmake(self):
        new_config = {}
        for key in self:
            val = self[key]
            if hasattr(val, "unmake"):
                val = val.unmake()
            new_config[key] = val
        return new_config
class ConfigList(ConfigObject, list):
    underlying = list
    def overwrites(self):
        self.commit_call(self.remove)
        self.commit_call(self.pop)
        self.commit_call(self.reverse)
    
    def insert(self, index, value):
        self.underlying.insert(self, index, self.wrap_object(value))
        self.commit()
    def append(self, value):
        self.underlying.append(self, self.wrap_object(value))
        self.commit()
    def extend(self, other):
        self.underlying.append(self, other)
        self.commit()
    
    def make(self, config):
        for item in config:
            self.append(self.wrap_object(item))
    def unmake(self):
        new_config = []
        for item in self:
            val = item
            if hasattr(val, "unmake"):
                val = val.unmake()
            new_config.append(val)
        return new_config

class ConfigManager(object):
    def __init__(self, directory="settings"):
        self.directory = os.path.join(current_directory, directory)
        self.configs = {}
        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)
    
    def list_configs(self, prefix=""):
        config_names = []
        for filename in glob.glob(os.path.join(self.directory, "*.conf")):
            config_names.append(os.path.basename(filename)[:-5])
        return config_names
    
    def open_config(self, filename):
        filename_conf = "%s.conf" % filename
        filename_temp = "%s.temp" % filename
        #if os.path.isfile(filename_temp):
        #    os.rename(filename_temp, filename_conf)
        # the above was bad, need to rethink this.
        if os.path.isfile(filename_conf):
            with open(filename_conf) as file_object:
                return yaml.load(file_object.read())
        return {}
    
    def commit(self, config, filename):
        filename_conf = "%s.conf" % filename
        filename_temp = "%s.temp" % filename
        with open(filename_temp, "w") as file_object:
            file_object.write(yaml.dump(config.unmake(),
                default_flow_style=False))
            file_object.flush()
            os.fsync(file_object.fileno())
        os.rename(filename_temp, filename_conf)
    
    def get_config(self, name):
        name = name.lower()
        if not name in self.configs:
            filename = os.path.join(self.directory, name)
            config = ConfigDictionary(self.open_config(filename) or {}, self)
            config.filename = filename
            self.configs[name] = config
        return self.configs[name]
