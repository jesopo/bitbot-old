

class Module(object):
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("to").hook(
            self.to, min_args=2)
        bot.events.on("received").on("message").on("channel"
            ).hook(self.channel_message)
    
    def to(self, event):
        target = event["args_split"][0].lower()
        text = " ".join(event["args_split"][1:])
        sender = event["sender"].nickname
        with event["channel"].config as config:
            if not "to" in config:
                config["to"] = {}
            if not target in config["to"]:
                config["to"][target] = []
            config["to"][target].append([sender, text])
        return "Saved."
    
    def waiting_messages(self, channel, nickname):
        messages = channel.config.get("to", {}).pop(nickname.lower(), [])
        for sender, text in messages[:]:
            messages.pop(0)
            channel.send_message("[To] %s: <%s> %s" % (nickname, sender,
                text))
        if "to" in channel.config and len(channel.config["to"]) == 0:
            del channel.config["to"]
        
    
    def channel_message(self, event):
        self.waiting_messages(event["channel"], event["sender"].nickname)