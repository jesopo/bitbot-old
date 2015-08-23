import json
import Utils

WORDNIK_URL = "http://api.wordnik.com:80/v4/word.json/%s/definitions"

class Module(object):
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("define"
            ).hook(self.define, min_args=1)
    
    def define(self, event):
        api_key = self.bot.config.get("wordnik-api-key", None)
        if not api_key:
            event["output"].write("No wordnik api key set.")
            return
        page = Utils.get_url(WORDNIK_URL % event["args_split"][0],
            get_params={"useCanonical": True, "limit": 1,
            "sourceDictionaries": "wiktionary", "api_key": api_key})
        if page:
            page = json.loads(page)
        else:
            return "Failed to load results"
        if len(page):
            return "%s: %s" % (page[0]["word"], page[0]["text"])
        return "No results found"