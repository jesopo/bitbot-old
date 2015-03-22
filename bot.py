import select
import ConfigManager, IRCServer

config_manager = ConfigManager.ConfigManager("servers")
servers = []

for config_filename in config_manager.list_configs():
    config = ConfigManager.Config(config_filename)
    server = IRCServer.IRCServer(config)
    servers.append(server)

for server in servers:
    server.connect()

write_waiting = set([])

while len(servers):
    readable, writable, errors = select.select(servers, write_waiting, [])
    for server in readable:
        line = server.read_line()
        # DO STUFF WITH THE LINE IDK
        print(line)
    for server in writable:
        server.send_line()
        write_waiting.remove(server)
    for server in servers:
        if server.waiting_send():
            write_waiting.add(server)