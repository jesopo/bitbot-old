import select
import ConfigManager, IRCServer, ModuleManager

class Bot(object):
    def __init__(self):
        self.module_manager = ModuleManager.ModuleManager()
        self.module_manager.load_modules()
        self.events = self.module_manager.events
        self.config_manager = ConfigManager.ConfigManager("servers")
        self.servers = []
        self.write_waiting = set([])
        
        configs = []
        for config_filename in self.config_manager.list_configs():
            config = ConfigManager.Config(config_filename)
            configs.append(config)
        for config in configs:
            server = IRCServer.IRCServer(config, self.events)
            self.servers.append(server)
        for server in self.servers:
            server.connect();
    
    def listen(self):
        while len(self.servers):
            readable, writable, errors = select.select(self.servers,
                self.write_waiting, [])
            for server in readable:
                line = server.read_line()
                # DO STUFF WITH THE LINE IDK
                print(line)
            for server in writable:
                server.send_line()
                self.write_waiting.remove(server)
            for server in self.servers:
                if server.waiting_send():
                    self.write_waiting.add(server)

