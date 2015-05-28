

class IRCUser(object):
    def __init__(self, nickname, id, server):
        self.server = server
        self.id = id
        self.nickname = None
        self.change_nickname(nickname)
        self.server.users[self.id] = self
        self.channels = {}
        self._destroyed = False
    
    def add_channel(self, channel):
        if not channel.name_lower in self.channels:
            self.channels[channel.name_lower] = channel
        channel.add_user(self)
    def _remove_channel(self, channel):
        if channel.name_lower in self.channels:
            del self.channels[channel.name_lower]
        channel.remove_user(self)
    def remove_channel(self, channel):
        self._remove_channel(channel)
        if len(self.channels.keys()) == 0:
            self.destroy()
    
    def change_nickname(self, nickname):
        self.server.nickname_to_id[nickname.lower()] = self.id
        if self.nickname:
            del self.server.nickname_to_id[self.nickname.lower()]
        self.nickname = nickname
        self.nickname_lower = nickname.lower()
    
    def send_who(self):
        self.server.send_who(self.nickname)
    def send_whois(self):
        self.server.send_whois(self.nickname)
    def send_message(self, text):
        self.server.send_message(self.nickname, text)
    def send_notice(self, text):
        self.server.send_notice(self.nickname, text)
    
    def destroy(self):
        for channel in list(self.channels.values()):
            self._remove_channel(channel)
        self._destroyed = True
        self.server.bot.events.on("destroyed").on("user").call(user=self)
    def is_destroyed(self):
        return self._destroyed