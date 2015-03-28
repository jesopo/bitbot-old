import glob, os
import yaml

current_directory = os.path.dirname(os.path.abspath(__file__))

class Config(object):
    def __init__(self, name):
        self.name = name
        self.config = None
        self.read()
    
    def read(self):
        if os.path.isfile(self.name):
            with open(self.name) as file_object:
                self.config = yaml.load(file_object.read())
    
    def save(self):
        with open(self.name, "w") as file_object:
            file_object.write(yaml.dump(self.config))
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def __getitem__(self, key):
        return self.config[key]
    def __setitem__(self, key, value):
        self.config[key] = value
    def __delitem__(self, key):
        del self.config[key]
    def __contains__(self, key):
        return key in self.config
    def __len__(self):
        return len(self.config)
    
    def __exit__(self, e_type, e_value, e_traceback):
        self.save()

class ConfigManager(object):
    def __init__(self, directory="settings"):
        self.directory = os.path.join(current_directory, directory)
        self.configs = {}
        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)
    
    def list_configs(self, prefix=""):
        return glob.glob("%s/*.conf" % self.directory)
    
    def get_config(self, name):
        if not name.lower() in self.configs:
            with open(name) as file_object:
                config = yaml.load(file_object.read())
                self.configs[name.lower()] = config
        return self.configs[name.lower()]