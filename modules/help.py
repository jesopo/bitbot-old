

class Module(object):
    _name = "Help"
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("help").hook(
            self.help, min_args=1)
    
    def help(self, event):
        if event["command"] in self.bot.events.on("received").on("command"):
            for function, _, options in self.bot.events.on("received").on(
                    "command").on(event["args_split"][0]).get_hooks():
                print(options)
                if "help" in options:
                    return "(%s) %s" % (event["args_split"][0],
                        options["help"])
            return "No help found"
        else:
            return "Command not found"