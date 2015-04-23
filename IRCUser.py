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
        channel.add_user(self)
    def part_channel(self, channel):
        if channel.name in self.channels:
            del self.channels[channel.name]
        channel.remove_user(self)
    
    def change_nickname(self, nickname):
        self.server.nickname_to_id[nickname.lower()] = self
        del self.server.nickname_to_id[self.nickname.lower()]
        self.nickname = nickname
    
    def send_who(self):
        self.server.send_who(self.nickname)
    def send_message(self, text):
        self.server.send_message(self.nickname, text)
    
    def destroy(self):
        del self.server.users[self.id]
        del self.server.nickname_to_id[self.nickname.lower()]
        for channel_name in list(self.channels.keys()):
            self.channels[channel_name].remove_user(self)
            del self.channels[channel_name]