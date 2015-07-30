import re

REGEX_KARMA = re.compile("^([^,:\s]+)[:,]?\s*(\+\+|--)")

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("message").on("channel").hook(
            self.on_message)
    
    def make_user(self, server, nickname):
        with server.config as config:
            if not "users" in config:
                config["users"] = {}
            if not nickname.lower() in config["users"]:
                config["users"][nickname.lower()] = {}
            if not "karma" in config["users"][nickname.lower()]:
                config["users"][nickname.lower()]["karma"] = 0
    
    def get_karma(self, server, nickname):
        return server.config.get("users", {}).get(nickname.lower(), {}
            ).get("karma", 0)
    
    def change_karma(self, server, nickname, operand):
        self.make_user(server, nickname)
        karma = 0
        if operand == "++":
            karma = 1
        elif operand == "--":
            karma = -1
        server.config["users"][nickname.lower()]["karma"] += karma
    
    def on_message(self, event):
        match = re.search(REGEX_KARMA, event["text"])
        if match:
            self.change_karma(event["server"], match.group(1), match.group(2))
    
    def karma(self, event):
        target = ""
        if event["args_split"]:
            target = event["args_split"][0]
        else:
            target = event["sender"].nickname
        return "%s has %d karma" % (target, self.get_karma(event["server"], target))