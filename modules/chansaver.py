

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("numeric").on("001").hook(self.on_connect)
        
    def on_connect(self, event):
        if event["server"].config.get("channels"):
            for channel in event["server"].config["channels"]:
                event["server"].send_join(channel)