import re, time
import Utils

REGEX_DURATION = re.compile("(\d+)([wdhms])", re.I)
duration_modifiers = {"w": Utils.TIME_WEEK, "d": Utils.TIME_DAY, "h": Utils.TIME_HOUR,
    "m": Utils.TIME_MINUTE, "s": Utils.TIME_SECOND}

class Module(object):
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("in").hook(
            self._in, min_args=2, help="Set a timed reminder")
        self.load()
    
    def load(self):
        for server_name in self.bot.configs:
            config = self.bot.configs[server_name]
            for channel_name in config.get("channels", {}):
                for due_at, target, message in (config["channels"][
                        channel_name] or {}).get("in", []):
                    if not self.make_timer(server_name, channel_name, due_at,
                            target, message):
                        self.remove_config(server_name, channel_name, due_at,
                            target, message)
    
    def remove_config(self, server_name, channel_name, due_at, target, message):
        config = self.bot.configs.get(server_name, {}).get("channels", {}).get(
            channel_name, None)
        if config:
            alert = [due_at, target, message]
            config = config.get("in", [])
            if alert in config:
                config.remove(alert)
    
    def make_timer(self, server_name, channel_name, due_at, target, message):
        delay = due_at-time.time()
        if delay > 0:
            self.bot.add_timer(self.timer_tick, delay, server_name=server_name,
                channel_name=channel_name, message=message, target=target,
                due_at=due_at)
            return True
        return False
    
    def _in(self, event):
        duration_string = event["args_split"][0]
        full_duration = 0
        for match in re.findall(REGEX_DURATION, duration_string):
            duration, modifier = match
            full_duration += int(duration)*duration_modifiers[modifier]
        if full_duration:
            target = nickname=event["sender"].nickname
            due_at = time.time()+full_duration
            message = " ".join(arg for arg in event["args_split"][1:])
            with event["channel"].config as config:
                if not "in" in config:
                    config["in"] = []
                config["in"].append([due_at, target, message])
                self.make_timer(event["server"].name, event["channel"].name, due_at,
                    target, message)
            return "Will do"
        return "Duration must be above 0 seconds"
    
    def timer_tick(self, timer, **kwargs):
        server = self.bot.servers.get(kwargs["server_name"], None)
        if server:
            channel = server.channels.get(kwargs["channel_name"], None)
            if channel:
                channel.send_message("[In] %s: %s" % (kwargs["target"],
                    kwargs["message"]))
        self.remove_config(kwargs["server_name"], kwargs["channel_name"],
            kwargs["due_at"], kwargs["target"], kwargs["message"])
        timer.destroy()