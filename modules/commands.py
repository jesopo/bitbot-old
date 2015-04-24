import Utils

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
        
        bot.events.on("new").on("channel").hook(self.new_channel)
        
        bot.events.on("received").on("command").on("more").hook(self.more)
    
    def new_channel(self, event):
        event["channel"].command_more = None
    
    def set_callback(self, child):
        child.set_callback_handler(self.handle)
    
    def new_child(self, event):
        self.set_callback(event["child"])
    
    def send_response(self, text, channel, module_name):
        text = "[%s] %s" % (module_name, text)
        text_truncated = Utils.overflow_truncate(text)
        if not text == text_truncated:
            channel.command_more = [text.replace(text_truncated, "", 1
                ).lstrip(), module_name]
            text = "%s (more)" % text_truncated
        channel.send_message(text)
    
    def on_message(self, event):
        command_prefix = event["channel"].config.get("command-prefix", event[
            "server"].config.get("command-prefix", "!"))
        
        if not event["action"] and event["text"].startswith(command_prefix):
            command = event["text_split"][0].replace(command_prefix, "", 1)
            args_split = event["text_split"][1:]
            args = " ".join(args_split)
            
            self.bot.events.on("received").on("command").on(
                command).call(channel=event["channel"], sender=event["sender"],
                server=event["server"], args=args, args_split=args_split,
                command=command, line=event["line"],
                line_split=event["line_split"])
    
    def handle(self, function, options, event):
        if len(event["args_split"]) >= options.get("min_args", 0):
            # other checks maybe
            text = function(event)
            if text:
                text = text.replace("\r", "").replace("\n", " ").replace("  ", " ")
                self.send_response(text, event["channel"], function.__self__._name)
    
    def more(self, event):
        if event["channel"].command_more:
            text, module_name = event["channel"].command_more
            event["channel"].command_more = None
            self.send_response("(continued) %s" % text, event["channel"], module_name)