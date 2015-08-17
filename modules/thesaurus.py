import json
import Utils

THESAURUS_URL = "http://words.bighugelabs.com/api/2/%s/%s/json"

class Module(object):
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("synonym"
            ).hook(self.thesaurus, min_args=1, 
            help="Get synonyms for a given word")
        bot.events.on("received").on("command").on("antonym"
            ).hook(self.thesaurus, min_args=1, 
            help="Get antonyms for a given word")
    
    def get_page(self, word):
        page = Utils.get_url(THESAURUS_URL % (self.bot.config.get(
            "thesaurus-api-key"), word))
        if page:
            page = json.loads(page)
        return page
    
    def thesaurus(self, event):
        if not self.bot.config.get("thesaurus-api-key"):
            return "No thesaurus api key set"
        category = ""
        if event["command"] == "synonym":
            category = "syn"
        else:
            category = "ant"
        page = self.get_page(event["args_split"][0])
        if page:
            if len(page.keys()) > 1 and not len(event["args_split"]) > 1:
                return "Available categories for %s: %s" % (
                    event["args_split"][0], ", ".join(page.keys()))
            elif event["args_split"][1].lower() in page:
                words = page[event["args_split"][1].lower()].get(category)
                if words:
                    return "%s (%s): %s" % (event["args_split"][0],
                        event["args_split"][1].lower(), ", ".join(words))
            else:
                return "Category not found"
        return "No results found"
        