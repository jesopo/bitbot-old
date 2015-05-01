import re
from bs4 import BeautifulSoup
import Utils

REGEX_TRANSLATE_BETWEEN = re.compile("^(\S*):(\S*)$")

class Module(object):
    _name = "Translate"
    def __init__(self, bot):
        bot.events.on("received").on("command").on("translate"
            ).hook(self.translate, min_args=1)
        bot.events.on("received").on("command").on("tr"
            ).hook(self.translate, min_args=1)
        bot.events.on("received").on("command").on("translatebetween"
            ).hook(self.translate_between, min_args=2)
        bot.events.on("received").on("command").on("trb"
            ).hook(self.translate_between, min_args=2)
        bot.events.on("received").on("command").on("translatelist"
            ).hook(self.translate_list)
        bot.events.on("received").on("command").on("trl"
            ).hook(self.translate_list)
    
    def get_def(self, phrase, source_language, target_language):
        page = Utils.get_url("https://translate.google.co.uk/", post_params={
            "sl": source_language, "tl": target_language, "js": "n",
            "prev": "_t", "hl": "en", "ie": "UTF-8", "text": phrase,
            "file": "", "edit-text": ""}, method="POST")
        if page:
            soup = BeautifulSoup(page)
            languages_element = soup.find(id="gt-otf-switch")
            translated_element = soup.find(id="result_box").find("span")
            if languages_element and translated_element:
                source_language, target_language = languages_element.attrs[
                    "href"].split("&sl=", 1)[1].split("&tl=", 1)
                target_language = target_language.split("&", 1)[0]
                translated = translated_element.text
                return source_language, target_language, translated
        return None, None, None
    
    def translate(self, event):
        source_language, target_language, translated = self.get_def(
            event["args"], "auto", "en")
        if source_language and target_language and translated:
            return "(%s > %s) %s" % (source_language, target_language,
                translated)
        else:
            return "Unable to translate"
    
    def translate_between(self, event):
        match = re.search(REGEX_TRANSLATE_BETWEEN, event["args_split"][0])
        if match and (match.group(1) or match.group(2)):
            source_language = match.group(1) or "auto"
            target_language = match.group(2) or "en"
            source_language, target_language, translated = self.get_def(
                " ".join(event["args_split"][1:]), source_language,
                target_language)
            if source_language and target_language and translated:
                return "(%s > %s) %s" % (source_language, target_language,
                    translated)
            else:
                return "Unable to translate"
        else:
            return "Please provide either a source language or target language as first argument; sl:tr, sl: or :tr."
    
    def translate_list(self, event):
        return "https://cloud.google.com/translate/v2/using_rest#language-params"