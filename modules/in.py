import re
import Utils

REGEX_DURATION = re.compile("(\d+)([wdhms])", re.I)
duration_modifiers = {"w": Utils.TIME_WEEK, "d": Utils.TIME_DAY, "h": Utils.TIME_HOUR,
    "m": Utils.TIME_MINUTE, "s": Utils.TIME_SECOND}

class Module(object):
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("in").hook(
            self._in, min_args=2)
    
    def _in(self, event):
        duration_string = event["args_split"][0]
        full_duration = 0
        for match in re.findall(REGEX_DURATION, duration_string):
            duration, modifier = match
            full_duration += int(duration)*duration_modifiers[modifier]
        if full_duration:
            self.bot.add_timer(self.timer_tick, full_duration, channel=event["channel"],
                nickname=event["sender"].nickname, message=" ".join(arg for arg in event[
                "args_split"][1:]))
            return "Will do"
        return "Duration must be above 0 seconds"
    
    def timer_tick(self, timer, **kwargs):
        kwargs["channel"].send_message("[In] %s: %s" % (kwargs["nickname"],
            kwargs["message"]))
        timer.destroy()