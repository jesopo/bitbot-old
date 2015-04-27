import datetime

class Module(object):
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("message").on("private"
            ).hook(self.private_message)
    
    def private_message(self, event):
        if event["text"].startswith("\01") and event["text"
                ].endswith("\01"):
            ctcp_args = event["text"][1:][:-1]
            ctcp_args_split = ctcp_args.split()
            command = ctcp_args_split[0].upper()
            if command == "VERSION":
                event["sender"].send_notice("\01VERSION %s\01" %
                    self.bot.config.get("ctcp-version",
                    "BitBot (https://github.com/jesopo/bitbot)"))
            elif command == "SOURCE":
                event["sender"].send_notice("\01SOURCE %s\01" %
                    self.bot.config.get("ctcp-source",
                    "https://github.com/jesopo/bitbot"))
            elif command == "PING" and len(ctcp_args_split) > 1:
                event["sender"].send_notice("\01PING %s\01" %
                    " ".join(ctcp_args_split[1:]))
            elif command == "TIME":
                event["sender"].send_notice("\01TIME %s\01" %
                    datetime.datetime.now().strftime("%c"))