

class module(object):
    def __init__(self, events):
        events.on("received").on("numeric").on("001").hook(self.on_connect)
        
    def on_connect(self, event):
        if "channels" in event["server"].config:
            for channel in event["server"].config["channels"]:
                event["server"].send_join(channel)