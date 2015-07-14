

class Module(object):
    _name = "Help"
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("help").hook(
            self.help)
    
    def help(self, event):
        if not len(event["args_split"]):
            commands = []
            for command, hook in self.bot.events.on("received").on("command"
                    ).get_children().items():
                for callback, _, options in self.bot.events.on("received").on(
                        "command").on(command).get_hooks():
                    if "help" in options:
                        commands.append(command)
                        break
            if commands:
                return "Available commands: %s" % ", ".join(commands)
            else:
                return "No help Available."
        elif event["command"] in self.bot.events.on("received").on("command"):
            for function, _, options in self.bot.events.on("received").on(
                    "command").on(event["args_split"][0]).get_hooks():
                print(options)
                if "help" in options:
                    return "(%s) %s" % (event["args_split"][0],
                        options["help"])
            return "No help found"
        else:
            return "Command not found"