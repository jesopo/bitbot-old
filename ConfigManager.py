import glob, os
import yaml

current_directory = os.path.dirname(os.path.abspath(__file__))

class Config(object):
    def __init__(self, path):
        self.path = path
        self.config = {}
        self.read()
    
    def read(self):
        if os.path.isfile(self.path):
            with open(self.path) as file_object:
                self.config = yaml.load(file_object.read())
    
    def save(self):
        with open(self.path, "w") as file_object:
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
        config_names = []
        
        for filename in glob.glob(os.path.join(self.directory, "*.conf")):
            config_names.append(os.path.basename(filename)[:-5])
        return config_names
    
    def get_config(self, name):
        name = name.lower()
        if not name in self.configs:
            self.configs[name] = Config("%s.conf" % os.path.join(self.directory, name))
        return self.configs[name]