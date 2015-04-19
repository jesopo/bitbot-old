import json, re
import ModuleHelpers

URBANDICTIONARY_URL = "http://api.urbandictionary.com/v0/define"
REGEX_NUMBER = re.compile(" -n ?(\d+)$")
REGEX_MAX_LENGTH = re.compile(".{1,300}(?=\s|$)")

class Module(object):
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
        page = ModuleHelpers.get_url(URBANDICTIONARY_URL, term=term)
        if page:
            page = json.loads(page)
        else:
            return "Failed to get definition"
        if number >= 0 and len(page["list"]) > number:
            definition = page["list"][number]
            text = "%s: %s" % (definition["word"], definition["definition"
                ].strip().replace("\n", "").replace("\r",""))
            length_match = re.match(REGEX_MAX_LENGTH, text)
            if length_match and not text == length_match.group(0):
                text = "%s... (%s)" % (length_match.group(), definition[
                    "permalink"])
            return text
        else:
            return "Definition number does not exist"