

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("command").on(
            "ping").hook(self.ping, help="Pong!")
    
    def ping(self, event):
        pong = "pong!"
        if event["args"]:
            pong = "%s %s" % (event["args"], pong)
        return ["Ping", pong]