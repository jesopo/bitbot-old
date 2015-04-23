import json
import ModuleHelpers

MEDIAWIKI_URL = "http://en.wikipedia.org/w/api.php"

class Module(object):
    _name = "MediaWiki"
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("wiki").hook(self.wiki,
            min_args=1)

    def wiki(self, event):
        title = event["args"]
        page = ModuleHelpers.get_url(MEDIAWIKI_URL, format="json",
            action="query", prop="extracts", exintro="", explaintext="",
            titles=title)
        if page:
            page = json.loads(page)
        else:
            return "Failed to load page"
        for i in page["query"]["pages"]:
            try:
                extract = page["query"]["pages"][i]["extract"]
                return extract[:extract.index(".") + 1] #Only the first sentence
            except ValueError:
                if len(extract) < 100:
                    return extract
                else:
                    return extract[:100]
            except KeyError:
                pass
        return "No wiki page found!"

