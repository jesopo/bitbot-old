

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("numeric").on("001").hook(
            self.on_connect)
    
    def on_connect(self, event):
        print(event["server"].config.get("perform", []))
        for command in event["server"].config.get("perform", []):
            new_command = []
            for part in command.split("%%"):
                new_command.append(part.replace("%nick%", event[
                    "server"].nickname))
            new_command = "%".join(new_command)
            event["server"].queue_line(new_command)
                