import time
import Utils

class Module(object):
    def __init__(self, bot):
        self.changed = {}
        bot.events.on("received").on("message").on("channel"
            ).hook(self.channel_message)
        bot.events.on("received").on("command").on("seen"
            ).hook(self.seen, min_args=1)
        bot.events.on("received").on("command").hook(
            self.channel_message)
        # todo: make this delay configurable
        bot.add_timer(self.on_timer, 20)
    
    def channel_message(self, event):
        if not event["channel"] in self.changed:
            self.changed[event["channel"]] = {}
        self.changed[event["channel"]][event["sender"].nickname.lower()
            ] = int(time.time())
    
    def on_timer(self, timer):
        for channel in self.changed:
            with channel.config as config:
                if not "seen" in config:
                    config["seen"] = {}
                for nickname in self.changed[channel]:
                    config["seen"][nickname] = self.changed[
                        channel][nickname]
    
    def seen(self, event):
        nickname = event["args_split"][0]
        nickname_lower = nickname.lower()
        timestamp = self.changed.get(event["channel"], {}).get(
            nickname_lower)
        timestamp = timestamp or event["channel"].config.get("seen",
            {}).get(nickname_lower)
        if timestamp:
            seconds_since = time.time()-timestamp
            since, unit = Utils.time_unit(seconds_since)
            return "%s was last seen %d %s ago." % (nickname, since, unit)
        return "I've never seen that user."