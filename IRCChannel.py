import IRCChannelMode

class IRCChannel(object):
    def __init__(self, name, server, config):
        self.name = name
        self.server = server
        self.config = config
        self.users = {}
        self.modes = {}
        self.user_modes = {}
        self.log = []
    
    def add_user(self, user):
        if not user.id in self.users:
            self.users[user.id] = user
        if not user.id in self.user_modes:
            self.user_modes[user.id] = set([])
    def remove_user(self, user):
        if user.id in self.users:
            del self.users[user.id]
        if user.id in self.user_modes:
            del self.user_modes[user.id]
    
    def add_mode(self, mode, argument):
        if not mode in self.modes:
            self.modes[mode] = IRCChannelMode.IRCChannelMode(self, mode)
        if argument:
            user = self.server.get_user_by_nickname(argument)
            if user and user.id in self.users:
                self.modes[mode].add_argument(user.id)
                self.user_modes[user.id].add(mode)
            else:
                self.modes[mode].add_argument(argument)
        else:
            self.modes[mode].enabled = True
    
    def remove_mode(self, mode, argument):
        if mode in self.modes:
            if argument:
                user = self.server.get_user_by_nickname(argument)
                if user and user.id in self.users:
                    self.modes[mode].remove_argument(user.id)
                    self.user_modes[user.id]
                else:
                    self.modes[mode].remove_argument(argument)
            else:
                self.modes[mode].enabled = False
    
    def send_who(self):
        self.server.send_who(self.name)
    def send_message(self, message):
        self.server.send_message(self.name, message)