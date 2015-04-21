

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("numeric").on("001").hook(
            self.on_connect)
    
    def on_connect(self, event):
        if "nickserv-password" in event["server"].config:
            event["server"].send_message("nickserv",
                "identify %s" % event["server"].config["nickserv-password"])