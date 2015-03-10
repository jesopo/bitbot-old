import uuid

class IRCUser(object):
    def __init__(self, nickname, server):
        self.nickname = nickname
        self.server = server
        self.id = None
        while not self.id or self.id in self.server.users:
            self.id = uuid.uuid1().hex
        self.server.users[self.id] = self
        self.server.nickname_to_id[self.nickname.lower()] = self.id
        self.channels = {}
    
    def join_channel(self, channel):
        if not channel.name in self.channels:
            self.channels[channel.name] = channel
    def part_channel(self, channel):
        if channel.name in self.channels:
            del self.channels[channel.name]
    
    def destroy(self):
        del self.server.users[self.id]
        del self.server.nickname_to_id[self.nickname.lower()]
        for channel in self.channels:
            channel.remove_user(self)
    