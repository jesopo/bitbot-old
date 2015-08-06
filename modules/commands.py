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
        bot.events.on("received").on("message").on("private").hook(
            self.on_private_message)
        
        bot.events.on("new").on("channel").hook(self.new_target)
        bot.events.on("new").on("user").hook(self.new_target)
        
        bot.events.on("received").on("command").on("more").hook(self.more,
            helf="Show text truncated from the last command's response")
        bot.events.on("received").on("command").on("pipelast").hook(
            self.pipe_last, min_args=1, help="Pipe the output of the last command"
            " to a supplied command")
    
    def new_target(self, event):
        target = event.get("channel", None)
        target = target or event.get("user")
        if target:
            target.command_more = None
            target.command_last = None
    
    def set_callback(self, child):
        child.set_callback_handler(self.handle)
    
    def new_child(self, event):
        self.set_callback(event["child"])
    
    def send_response(self, text, target, module_name):
        command_text = "[%s] %s" % (module_name, text)
        command_text_truncated = Utils.overflow_truncate(command_text)
        if not command_text == command_text_truncated:
            target.command_more = [command_text.replace(
                command_text_truncated, "", 1), module_name]
            command_text = "%s (more)" % command_text_truncated.rstrip(" ")
        target.command_last = command_text.replace("[%s] " % module_name,
            "", 1)
        target.send_message(command_text)
    
    def on_private_message(self, event):
        command = event["text_split"][0].lower()
        args_split = event["text_split"][1:]
        args = " ".join(args_split)
        self.bot.events.on("received").on("command").on(command).call(
            sender=event["sender"], server=event["server"], args=args,
            args_split=args_split, command=command, line=event["line"],
            line_split=event["line_split"], target=event["sender"],
            is_channel=False)
    
    def on_message(self, event):
        command_prefix = event["channel"].config.get("command-prefix", event[
            "server"].config.get("command-prefix", "!"))
        
        if not event["action"] and event["text"].startswith(command_prefix):
            command = event["text_split"][0].replace(command_prefix, "", 1
                ).lower()
            event.stop_propagation()
            args_split = event["text_split"][1:]
            args = " ".join(args_split)
            
            self.bot.events.on("received").on("command").on(
                command).call(channel=event["channel"], sender=event["sender"],
                server=event["server"], args=args, args_split=args_split,
                command=command, line=event["line"], is_channel=True,
                line_split=event["line_split"], target=event["channel"])
    
    def handle(self, function, options, event):
        module_name = function.__self__._name
        if options.get("channel_only", False) and not event["is_channel"]:
            return False
        if options.get("private_only", False) and event["is_channel"]:
            return False
        if len(event["args_split"]) < options.get("min_args", 0):
            self.send_response("Not enough arguments.", event["target"],
                function.__self__._name)
            return
        for returned in self.bot.events.on("event").on("command").call(
                function=function, options=options, event=event).get_all():
            if returned:
                self.send_response(returned, event["target"], module_name)
                return False
        # other checks maybe
        returned = function(event)
        if returned:
            text = returned
            
            if not type(returned) in [str, bytes] and len(returned) > 1:
                module_name = returned[0]
                text = returned[1]
            
            text = text.replace("\r", "").replace("\n", " ")
            self.send_response(text, event["target"], module_name)
    
    def more(self, event):
        if event["channel"].command_more:
            text, module_name = event["channel"].command_more
            event["channel"].command_more = None
            self.send_response("(continued) %s" % text, event["channel"], module_name)
    
    def pipe_last(self, event):
        if event["channel"].command_last:
            command = event["args_split"][0].lower()
            kwargs = event.kwargs()
            kwargs["command"] = command
            kwargs["args"] = event["channel"].command_last
            kwargs["args_split"] = kwargs["args"].split(" ")
            self.bot.events.on("received").on("command").on(command).call(
                **kwargs)