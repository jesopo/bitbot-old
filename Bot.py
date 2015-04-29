import select
import ConfigManager, IRCServer, ModuleManager, TimedCallback

class Bot(object):
    def __init__(self):
        self.servers = set([])
        self.other_fds = set([])
        self.write_waiting = set([])
        self.module_manager = ModuleManager.ModuleManager(self)
        self.events = self.module_manager.events
        self.module_manager.load_modules()
        self.server_config_manager = ConfigManager.ConfigManager("servers")
        self.general_config_manager = ConfigManager.ConfigManager("settings")
        self.timed_callbacks = []
        
        self.config = self.general_config_manager.get_config("bot")
        
        configs = []
        for config_name in self.server_config_manager.list_configs():
            config = self.server_config_manager.get_config(config_name)
            configs.append(config)
        for config in configs:
            server = IRCServer.IRCServer(config, self)
            self.events.on("new").on("server").call(server=server)
            self.servers.add(server)
        for server in self.servers:
            server.connect()
    
    def get_soonest_timer(self):
        soonest = None
        for timer in self.timed_callbacks[:]:
            if timer.is_destroyed():
                self.timed_callbacks.remove(timer)
            elif soonest == None or timer.due_at() < soonest.due_at():
                soonest = timer
        return soonest
    def get_timer_delay(self):
        soonest = self.get_soonest_timer()
        if not soonest:
            return self.config.get("max-loop-interval", 4)
        return soonest.time_until()
    def add_timer(self, function, delay, *args, **kwargs):
        timer = TimedCallback.Timer(function, delay, *args, **kwargs)
        self.timed_callbacks.append(timer)
    def call_timers(self):
        for timer in self.timed_callbacks:
            if timer.due():
                timer.call()
    
    def reconnect(self, server):
        self.servers.remove(server)
        server.disconnect()
        new_server = IRCServer.IRCServer(server.config, self.events)
        self.events.on("new").on("server").call(server, new_server)
        self.servers.add(new_server)
    
    def listen(self):
        while len(self.servers):
            readable, writable, errors = select.select(self.servers|
                self.other_fds, self.write_waiting, [], self.get_timer_delay())
            self.call_timers()
            for server in readable:
                if server in self.other_fds:
                    self.events.on("other_fd").on("readable").on(
                        server.fileno()).call(readable=server)
                if server in self.servers:
                    lines = server.read_lines()
                    if lines:
                        for line in lines:
                            if line:
                                if self.config.get("verbose", True):
                                    print(line)
                    else:
                        self.reconnect(server)
            for server in writable:
                if server in self.other_fds:
                    self.events.on("other_fds").on("writable").on(
                        server.fileno()).call(writable=server)
                if server in self.servers:
                    server.send_line()
                self.write_waiting.remove(server)
            for server in self.servers:
                if server.waiting_send():
                    self.write_waiting.add(server)

