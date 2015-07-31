

class Module(object):
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("help").hook(
            self.help, help="Show bot help")
    
    def help(self, event):
        if not event["args_split"]:
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
        elif event["args_split"][0].lower() in self.bot.events.on("received").on("command"):
            for function, _, options in self.bot.events.on("received").on(
                    "command").on(event["args_split"][0].lower()).get_hooks():
                if "help" in options:
                    return "(%s) %s" % (event["args_split"][0].lower(),
                        options["help"])
            return "No help found"
        else:
            return "Command not found"