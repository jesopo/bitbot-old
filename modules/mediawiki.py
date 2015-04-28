import json, re
import Utils

WIKIPEDIA_URL = "http://en.wikipedia.org/w/api.php"

class Module(object):
    _name = "MediaWiki"
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("wi").hook(self.wiki,
            min_args=1)
        bot.events.on("received").on("command").on("mw").hook(self.wiki,
            min_args=1)

    def wiki(self, event):
        title = event["args"]
        if event["command"] == "wi":
            wiki_url = WIKIPEDIA_URL
        else:
            wiki_url = event["server"].config.get("mediawiki", WIKIPEDIA_URL)
        page = Utils.get_url(wiki_url, get_params={"format": "json",
            "action": "query", "prop": "extracts", "exintro": "",
            "explaintext": "", "titles": title})
        if page:
            page = json.loads(page)
        else:
            return "Failed to load page"
        for i in page["query"]["pages"]:
            try:
                text = page["query"]["pages"][i]["extract"]
                assert text
                return text
            except (KeyError, AssertionError):
                pass
        return "No wiki page found!"
