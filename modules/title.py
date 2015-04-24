import re
import Utils

RE_TITLE = re.compile("<title>(.*?)</title>", re.I)
RE_URL = re.compile("https?://\S+", re.I)

class Module(object):
    _name = "Title"
    def __init__(self, bot):
        bot.events.on("received").on("command").on("t").hook(self.title)
        bot.events.on("received").on("command").on("title").hook(self.title)
    
    def find_last_url(self, target):
        if target:
            for log in target.log:
                match = re.search(RE_URL, log["text"])
                if match:
                    return match.group(0)
    
    def title(self, event):
        url = None
        if event["args_split"]:
            url = event["args_split"][0]
            if not url.startswith("http://"):
                url = "http://%s" % url
        else:
            url = self.find_last_url(event["channel"])
        
        if url:
            page = Utils.get_url(url)
            if page:
                title = re.search(RE_TITLE, page)
                if title:
                    return title.group(1)
                else:
                    return "could not find title."
            else:
                return "could not get page."
        else:
            return "no URL provided."