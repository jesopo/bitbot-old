import re, traceback, urllib.parse
import Utils

REGEX_TITLE = re.compile("<title>(.*?)</title>", re.I)
REGEX_URL = re.compile("https?://\S+", re.I)
# this horrific regex is to find soft-redirects
# e.g <meta http-equiv="refesh" content="0;url=/path/here">
REGEX_META_REFRESH = re.compile(
    "<meta(?:[^>]+?content=['\"]\d+;url=([^'\">]+)|[^>]+?http-equiv=['\"]refresh){2}",
    re.I)

class Module(object):
    _name = "Title"
    def __init__(self, bot):
        bot.events.on("received").on("command").on("t").hook(self.title)
        bot.events.on("received").on("command").on("title").hook(self.title)
    
    def find_last_url(self, target):
        if target:
            for log in target.log:
                match = re.search(REGEX_URL, log["text"])
                if match:
                    return match.group(0)
    
    def get_title(self, url):
        page = Utils.get_url(url)
        if page:
            title_match = re.search(REGEX_TITLE, page)
            if not title_match:
                meta_refresh_match = re.search(REGEX_META_REFRESH, page)
                print(page)
                print(meta_refresh_match)
                if meta_refresh_match:
                    return self.get_title(urllib.parse.urljoin(url,
                        meta_refresh_match.group(1)))
            else:
                return title_match.group(1)
    
    def title(self, event):
        url = None
        if event["args_split"]:
            url = event["args_split"][0]
            if not url.startswith("http://"):
                url = "http://%s" % url
        else:
            url = self.find_last_url(event["channel"])
        
        if url:
            title = self.get_title(url)
            if title:
                return title
            else:
                return "could not find title."
        else:
            return "no URL provided."