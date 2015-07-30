import select, sys, time, traceback
import ConfigManager, IRCServer, ModuleManager, TimedCallback

class Bot(object):
    def __init__(self):
        self.servers = {}
        self.other_fds = set([])
        self.write_waiting = set([])
        self.soonest_timer = None
        self.timed_callbacks = []
        self.new_timed_callbacks = []
        self.module_manager = ModuleManager.ModuleManager(self)
        self.events = self.module_manager.events
        self.server_config_manager = ConfigManager.ConfigManager("servers")
        self.general_config_manager = ConfigManager.ConfigManager("settings")
        
        self.config = self.general_config_manager.get_config("bot")
        
        self.configs = {}
        for config_name in self.server_config_manager.list_configs():
            config = self.server_config_manager.get_config(config_name)
            self.configs[config_name] = config
        
        self.module_manager.load_modules()
        
        for config_name in self.configs:
            server = IRCServer.IRCServer(config_name, self.configs[config_name], self)
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
        if len(self.new_timed_callbacks):
            for timer in self.new_timed_callbacks[:]:
                if not self.soonest_timer or timer.due_at() < self.soonest_timer.due_at():
                    self.soonest_timer = timer
                self.timed_callbacks.append(self.new_timed_callbacks.pop(
                    self.new_timed_callbacks.index(timer)))
        return self.soonest_timer
    def get_timer_delay(self):
        soonest = self.get_soonest_timer()
        if not soonest:
            return self.config.get("max-loop-interval", None)
        delay = soonest.due_at()-time.time()
        return delay if delay >= 0 else 0
    def add_timer(self, function, delay, *args, **kwargs):
        timer = TimedCallback.Timer(function, delay, *args, **kwargs)
        self.new_timed_callbacks.append(timer)
    def call_timers(self):
        if self.soonest_timer and self.soonest_timer.due():
            self.soonest_timer = None
            for timer in self.timed_callbacks[:]:
                if timer.due():
                    timer.call()
                if timer.is_destroyed():
                    self.timed_callbacks.remove(timer)
                elif not self.soonest_timer or timer.due_at() < self.soonest_timer.due_at():
                    self.soonest_timer = timer
    
    def reconnect(self, server):
        del self.servers[server.name]
        server.disconnect()
        new_server = IRCServer.IRCServer(server.name, server.config, self)
        new_server.connect()
        self.events.on("new").on("server").call(server=new_server)
        self.servers[new_server.name] = new_server
    
    def listen(self):
        while len(self.servers):
            for server in list(self.servers.values()):
                if not server.connected:
                    del self.servers[server.name]
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

