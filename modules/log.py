

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("message").on("channel").hook(self.channel)
        bot.events.on("received").on("message").on("private").hook(self.private)
    
    def make_log(self, event):
        log = {}
        log["text"] = event["text"]
        log["nickname"] = event["sender"].nickname
        log["action"] = event["action"]
        return log
    
    def do_log(self, log_list, log, server):
        log_list.append(log)
        while len(log_list) > self.server_max_log(server):
            log_list.pop(0)
    
    def server_max_log(self, server):
        return server.config.get("max-log", 64)
    
    def channel(self, event):
        if not hasattr(event["channel"], "log"):
            event["channel"].log = []
        log = self.make_log(event)
        self.do_log(event["channel"].log, log, event["server"])
    
    def private(self, event):
        if not hasattr(event["sender"], "log"):
            event["sender"].log = []
        log = self.make_log(event)
        self.do_log(event["sender"].log, log, event["server"])