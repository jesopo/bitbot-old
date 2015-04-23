

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("message").on("channel").hook(self.channel)
        
        bot.events.on("send").on("message").on("channel").hook(self.channel)
        
        bot.events.on("new").on("channel").hook(self.new_channel)
    
    def make_log(self, event):
        log = {}
        log["text"] = event["text"]
        log["nickname"] = event["sender"].nickname
        log["action"] = event["action"]
        log["self"] = event["sender"].nickname == event["server"].nickname
        return log
    
    def do_log(self, log_list, log, server):
        log_list.insert(0, log)
        while len(log_list) > self.server_max_log(server):
            log_list.pop(len(log_list)-1)
    
    def new_channel(self, event):
        event["channel"].log = []
    
    def server_max_log(self, server):
        return server.config.get("max-log", 64)
    
    def channel(self, event):
        log = self.make_log(event)
        self.do_log(event["channel"].log, log, event["server"])