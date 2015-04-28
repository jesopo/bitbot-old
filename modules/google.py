import json
import Utils

GOOGLE_URL = "https://www.googleapis.com/customsearch/v1"

class Module(object):
    _name = "Google"
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("google"
            ).hook(self.google, min_args=1)
        bot.events.on("received").on("command").on("g"
            ).hook(self.google, min_args=1)
    
    def google(self, event):
        api_key = self.bot.config.get("google-api-key")
        search_id = self.bot.config.get("google-search-id")
        if not api_key:
            return "no google api key set."
        if not search_id:
            return "no google search id set."
        page = Utils.get_url(GOOGLE_URL, get_params={"q": event["args"],
            "key": api_key, "cx": search_id, "prettyPrint": "true",
            "num": "1", "gl": "uk"})
        page = json.loads(page)
        if "items" in page and len(page["items"]):
            return page["items"][0]["link"]
        return "no results"