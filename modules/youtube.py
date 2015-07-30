import json
import Utils

YOUTUBE_URL = "https://www.googleapis.com/youtube/v3/search"
SHORT_URL = "https://youtu.be/%s"

class Module(object):
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("yt").hook(self.yt,
            help="Search for a video on youtube")
    
    def yt(self, event):
        api_key = self.bot.config.get("google-api-key")
        search_id = self.bot.config.get("google-search-id")
        if not api_key:
            return "no google api key set."
        if not search_id:
            return "no google search id set."
        page = Utils.get_url(YOUTUBE_URL, get_params={"q": event["args"],
            "key": api_key, "part": "snippet", "maxResults": 1, "type": "video"})
        page = json.loads(page)
        if len(page["items"]):
            snippet = page["items"][0]["snippet"]
            return "%s (posted by %s) %s " % (snippet["title"], snippet[
                "channelTitle"], SHORT_URL % page["items"][0]["id"]["videoId"])
        else:
            return "No results found"