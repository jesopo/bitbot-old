import re

class Log(object):
    def __init__(self, nickname, text, is_action, from_self):
        self.nickname = nickname
        self.text = text
        self.is_action = is_action
        self.from_self = from_self
    
    def matches_regex(self, pattern):
        return re.search(pattern, self.text)

class LogList(object):
    def __init__(self, server):
        self.server = server
        self._log_list = []
    
    def get(self, index):
        if len(self._log_list) > index:
            reversed_index = (len(self._log_list)-1)-index
            return self._log_list[reversed_index]
        return None
    
    def add(self, nickname, text, is_action, from_self):
        self._log_list.append(Log(nickname, text,is_action, from_self))
        if len(self._log_list) > self.server.config.get("max-log", 64):
            self._log_list.pop(0)
    
    def find_regex(self, pattern):
        for log in self:
            match = log.matches_regex(pattern)
            if match:
                return match
    
    def __iter__(self):
        if self._log_list:
            index = len(self._log_list)-1
            while index > -1:
                yield self._log_list[index]
                index -= 1

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("message").on("channel").hook(self.channel)
        
        bot.events.on("send").on("message").on("channel").hook(self.channel)
        
        bot.events.on("new").on("channel").hook(self.new_channel)
    
    def new_channel(self, event):
        event["channel"].log = LogList(event["server"])
    
    def channel(self, event):
        event["channel"].log.add(event["sender"].nickname, event["text"],
            event["action"], "send" in event)