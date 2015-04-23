

class Module(object):
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("_new_child").hook(
            self.new_child)
        for name, child in bot.events.on("received").on("command"
                ).get_children().items():
            self.set_callback(child)
        bot.events.on("received").on("message").on("channel").hook(
            self.on_message)
        bot.events.on("received").on("message").on("private").hook(
            self.on_message)
    
    def set_callback(self, child):
        child.set_callback_handler(self.handle)
    
    def new_child(self, event):
        self.set_callback(event["child"])
    
    def on_message(self, event):
        command_prefix = event["channel"].config.get("command-prefix", event[
            "server"].config.get("command-prefix", "!"))
        channel = event.get("channel")
        if not event["action"] and (not channel or event[
                "text"].startswith(command_prefix)):
            command = event["text_split"][0]
            if channel:
                command = command.replace(command_prefix, "", 1)
            args_split = event["text_split"][1:]
            args = " ".join(args_split)
            
            self.bot.events.on("received").on("command").on(
                command).call(channel=channel, sender=event["sender"],
                server=event["server"], args=args, args_split=args_split,
                command=command, line=event["line"],
                line_split=event["line_split"])
    
    def handle(self, function, options, event):
        if len(event["args_split"]) >= options.get("min_args", 0):
            # other checks maybe
            text = function(event)
            command_response = "[%s] %s" % (function.__self__._name, text)
            recipient = event["channel"] or event["sender"]
            recipient.send_message(command_response)