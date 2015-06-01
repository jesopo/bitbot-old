import scrypt
import base64, os

class Module(object):
    def __init__(self, bot):
        bot.events.on("event").on("command").hook(self.on_command)
    
    def on_command(self, event):
        if "permissions" in event["options"]:
            user_permissions = event["event"]["server"].config.get("registered", {}
                ).get(event["event"]["sender"].nickname_lower, {}).get(
                "permissions", [])
            for permission in event["options"]["permissions"]:
                if not permission in user_permissions:
                    return "You do not have permission to do this"