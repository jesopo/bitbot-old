import re, traceback
import xml.etree.ElementTree as etree
import Utils

REGEX_CHAR_HEX = re.compile("\\\\:(\S{4})")

WA_URL = "http://api.wolframalpha.com/v2/query"

class Module(object):
    _name = "WolframAlpha"
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("wa").hook(self.wa,
            min_args=1)
    
    def get_def(self, term):
        app_id = self.bot.config.get("wolframalpha-app-id")
        if not app_id:
            return "no wolframalpha app id set."
        page = Utils.get_url(WA_URL, get_params={"input": term,
            "appid": app_id, "format": "plaintext", "reinterpret": "true"
            })
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
                    if text == None or text.text == None:
                        continue
                    text = "(%s) %s" % (term.replace(" | ", ": "
                        ), text.text.strip().replace(" | ", ": "
                        ).replace("\n", " | ").replace("\r", ""))
                    while True:
                        match = re.search(REGEX_CHAR_HEX, text)
                        if not match:
                            break
                        text = re.sub(REGEX_CHAR_HEX, chr(int(match.group(1),
                            16)), text)
                    return text
                    
    
    def wa(self, event):
        answer = self.get_def(event["args"])
        if answer:
            return answer
        else:
            return "could not get definition."