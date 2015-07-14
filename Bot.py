import select, sys, traceback
import ConfigManager, IRCServer, ModuleManager, TimedCallback

class Bot(object):
    def __init__(self):
        self.servers = {}
        self.other_fds = set([])
        self.write_waiting = set([])
        self.timed_callbacks = []
        self.module_manager = ModuleManager.ModuleManager(self)
        self.events = self.module_manager.events
        self.module_manager.load_modules()
        self.server_config_manager = ConfigManager.ConfigManager("servers")
        self.general_config_manager = ConfigManager.ConfigManager("settings")
        
        self.config = self.general_config_manager.get_config("bot")
        
        configs = {}
        for config_name in self.server_config_manager.list_configs():
            config = self.server_config_manager.get_config(config_name)
            configs[config_name] = config
        for config_name in configs:
            server = IRCServer.IRCServer(config_name, configs[config_name], self)
            self.events.on("new").on("server").call(server=server)
            self.servers[config_name] = server
        for server in self.servers.values():
            try:
                server.connect()
            except:
                print("Failed to connect to %s:" % server.str_host)
                traceback.print_exc()
                sys.exit()
            if not server.connected:
                sys.exit()
    
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
        for timer in self.timed_callbacks[:]:
            if timer.is_destroyed():
                self.timed_callbacks.remove(timer)
            elif timer.due():
                timer.call()
    
    def reconnect(self, server):
        self.servers.remove(server)
        server.disconnect()
        new_server = IRCServer.IRCServer(server.name, server.config, self)
        self.events.on("new").on("server").call(server, new_server)
        self.servers.add(new_server)
    
    def listen(self):
        while len(self.servers):
            for server in list(self.servers.values()):
                if not server.connected:
                    self.servers.discard(server)
                    self.write_waiting.discard(server)
            readable, writable, errors = select.select(set(self.servers.values())|
                self.other_fds, self.write_waiting, [], self.get_timer_delay())
            self.call_timers()
            for server in readable:
                if server in self.other_fds:
                    self.events.on("other_fd").on("readable").on(
                        server.fileno()).call(readable=server)
                if server in self.servers.values():
                    lines = server.read_lines()
                    if not lines == None:
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
                if server in self.servers.values():
                    server.send_line()
                self.write_waiting.remove(server)
            for server in self.servers.values():
                if server.waiting_send():
                    self.write_waiting.add(server)

