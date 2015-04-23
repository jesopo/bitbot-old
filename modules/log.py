

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("message").on("channel").hook(self.channel)
        
        bot.events.on("send").on("message").on("channel").hook(self.channel)
    
    def make_log(self, event):
        log = {}
        log["text"] = event["text"]
        log["nickname"] = event["sender"].nickname
        log["action"] = event["action"]
        log["self"] = event["sender"].nickname == event["server"].nickname
        return log
    
    def do_log(self, log_list, log, server):
        log_list.append(log)
        while len(log_list) > self.server_max_log(server):
            log_list.pop(0)
    
    def create_log(self, target):
        if not hasattr(target, "log"):
            target.log = []
    
    def server_max_log(self, server):
        return server.config.get("max-log", 64)
    
    def channel(self, event):
        self.create_log(event["channel"])
        log = self.make_log(event)
        self.do_log(event["channel"].log, log, event["server"])