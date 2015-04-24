

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("numeric").on("001").hook(self.on_connect)
        
    def on_connect(self, event):
        for channel_name in event["server"].config.get("channels", {}):
            if (event["server"].config["channels"][
                    channel_name] or {}).get("autojoin", True):
                event["server"].send_join(channel_name)