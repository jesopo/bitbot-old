

class IRCChannelMode(object):
    def __init__(self, channel, mode):
        self.channel = channel
        self.mode = mode
        self.enabled = False
        self.arguments = set([])
    
    def add_argument(self, argument):
        self.arguments.add(argument)
    def remove_argument(self, argument):
        if argument in self.arguments:
            self.arguments.remove(argument)