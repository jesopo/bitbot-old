import json, time
import Utils

SOUNDCLOUD_URL = "http://api.soundcloud.com/tracks"
HELP_STRING = "Search soundcloud"

class Module(object):
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("soundcloud"
            ).hook(self.soundcloud, min_args=1, help=HELP_STRING)
        bot.events.on("received").on("command").on("sc"
            ).hook(self.soundcloud, min_args=1, help=HELP_STRING)
    
    def soundcloud(self, event):
        soundcloud_api_key = self.bot.config.get("soundcloud-api-key",
            None)
        if not soundcloud_api_key:
            return "no soundcloud api key set"
        page = Utils.get_url(SOUNDCLOUD_URL, get_params={
            "client_id": soundcloud_api_key, "limit": 1, "q":
            event["args"]})
        if page:
            page = json.loads(page)
        else:
            return "Failed to load results"
        if page:
            page = page[0]
            title = page["title"]
            user = page["user"]["username"]
            duration = time.strftime("%H:%M:%S", time.gmtime(page[
                "duration"]/1000))
            if duration.startswith("00:"):
                duration = duration[3:]
            link = page["permalink_url"]
            return "%s [%s] (posted by %s) %s" % (title, duration,
                user, link)