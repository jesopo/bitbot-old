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
                            target, message, True):
                        self.remove_config(server_name, channel_name, due_at,
                            target, message, True)
            for nickname in config.get("users", {}):
                for due_at, message in (config["users"][nickname] or {}
                        ).get("in", []):
                    if not self.make_timer(server_name, nickname, due_at,
                            nickname, message, False):
                        self.remove_config(server_name, nickname, due_at,
                            nickname, message, False)
    
    def remove_config(self, server_name, target_name, due_at, nickname, message,
            is_channel):
        server_config = self.bot.configs.get(server_name, {})
        if server_config:
            config = None
            alert = None
            if is_channel:
                config = server_config.get("channels", {}).get(target_name,
                    None)
                alert = [due_at, nickname, message]
            else:
                config = server_config.get("users", {}).get(target_name, None)
                alert = [due_at, message]
            if config:
                alert = [due_at, nickname, message]
                config = config.get("in", [])
                if alert in config:
                    config.remove(alert)
    
    def make_timer(self, server_name, target_name, due_at, nickname, message, is_channel):
        delay = due_at-time.time()
        if delay > 0:
            self.bot.add_timer(self.timer_tick, delay, server_name=server_name,
                target_name=target_name, message=message, nickname=nickname,
                due_at=due_at, is_channel=is_channel)
            return True
        return False
    
    def _in(self, event):
        duration_string = event["args_split"][0]
        full_duration = 0
        for match in re.findall(REGEX_DURATION, duration_string):
            duration, modifier = match
            full_duration += int(duration)*duration_modifiers[modifier]
        if full_duration:
            target = event["sender"].nickname
            due_at = time.time()+full_duration
            message = " ".join(arg for arg in event["args_split"][1:])
            target_config = None
            if event["is_channel"]:
                target_config = event["channel"].config
            else:
                if not event["sender"].name.lower() in event["server"].config["users"]:
                    event["server"].config["users"][event["sender"].name.lower()] = {}
                target_config = event["server"].config["users"][event["sender"].name.lower()]
            with target_config as config:
                if not "in" in config:
                    config["in"] = []
                if event["is_channel"]:
                    config["in"].append([due_at, target, message])
                else:
                    config["in"].append([due_at, message])
                self.make_timer(event["server"].name, event["target"].name, due_at,
                    target, message, event["is_channel"])
            return "Will do"
        return "Duration must be above 0 seconds"
    
    def timer_tick(self, timer, **kwargs):
        server = self.bot.servers.get(kwargs["server_name"], None)
        if server:
            target = server.get_channel(kwargs["target_name"])
            target = target or server.get_user_by_nickname(kwargs["target_name"])
            if target:
                if kwargs["is_channel"]:
                    target.send_message("[In] %s: %s" % (kwargs["nickname"],
                        kwargs["message"]))
                else:
                    target.send_message("[In] %s" % kwargs["message"])
        self.remove_config(kwargs["server_name"], kwargs["target_name"],
            kwargs["due_at"], kwargs["target_name"], kwargs["message"],
            kwargs["is_channel"])
        timer.destroy()