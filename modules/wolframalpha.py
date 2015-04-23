import traceback
import xml.etree.ElementTree as etree
import ModuleHelpers

WA_URL = "http://api.wolframalpha.com/v2/query"

class Module(object):
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("wa").hook(self.wa,
            min_args=1)
    
    def get_def(self, term):
        app_id = self.bot.config.get("wolframalpha-app-id")
        page = ModuleHelpers.get_url(WA_URL, input=term, appid=app_id,
            format="plaintext")
        if page:
            try:
                page = etree.fromstring(page)
            except:
                return
            term = page.find(".//pod[@id='Input']/subpod/plaintext")
            if term == None:
                return
            term = term.text
            definitions = page.findall(".//pod")
            if len(definitions) > 1:
                for definition in definitions[1:]:
                    text = definition.find(".//subpod/plaintext")
                    if text == None:
                        continue
                    return "(%s) %s" % (term.replace(" | ", ": "
                        ), text.text.strip().replace(" | ", ": "
                        ).replace("\n", " | ").replace("\r", ""))
    
    def wa(self, event):
        answer = self.get_def(event["args"])
        if answer:
            return answer
        else:
            return "could not get definition."