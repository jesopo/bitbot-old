import json, re
import Utils

URBANDICTIONARY_URL = "http://api.urbandictionary.com/v0/define"
REGEX_NUMBER = re.compile(" -n ?(\d+)$")

class Module(object):
    _name = "UrbanDictionary"
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("ud").hook(self.ud, min_args=
            1)
    
    def ud(self, event):
        number = 0
        match = re.search(REGEX_NUMBER, event["args"])
        term = event["args"]
        if match:
            number = int(match.group(1))-1
            term = re.sub(REGEX_NUMBER, "", term)
        page = Utils.get_url(URBANDICTIONARY_URL, term=term)
        if page:
            page = json.loads(page)
        else:
            return "Failed to get definition"
        if number >= 0 and len(page["list"]) > number:
            definition = page["list"][number]
            text = "%s: %s" % (definition["word"], definition["definition"
                ].strip())
            return text
        else:
            return "Definition number does not exist"
