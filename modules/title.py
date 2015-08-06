import re, traceback, urllib.parse
from bs4 import BeautifulSoup
import Utils

REGEX_TITLE = re.compile("<title>(.*?)</title>", re.I|re.S)
REGEX_URL = re.compile("https?://\S+", re.I)
REGEX_UNICODE_CODEPOINT = re.compile(r"\\u(\d{4})", re.I)
HELP_STRING = "Get the title from a supplied url"

class Module(object):
    _name = "Title"
    def __init__(self, bot):
        bot.events.on("received").on("command").on("t").hook(self.title,
            help=HELP_STRING)
        bot.events.on("received").on("command").on("title").hook(self.title,
            help=HELP_STRING)
    
    def find_last_url(self, target):
        if target:
            for log in target.log:
                match = re.search(REGEX_URL, log.text)
                if match:
                    return match.group(0)
    
    def get_title(self, url):
        page = Utils.get_url(url)
        if page:
            page = BeautifulSoup(page)
            title = page.title.text
            if title:
                title = title.replace("\n", " ").replace("  ", " ").strip()
                for match in re.finditer(REGEX_UNICODE_CODEPOINT, title):
                    title = title.replace(match.group(0), chr(int(match.group(1), 16)))
            return title
    
    def title(self, event):
        url = None
        if event["args_split"]:
            url = event["args_split"][0]
            if not url.startswith("https://") and not url.startswith(
                    "http://"):
                url = "http://%s" % url
        else:
            url = self.find_last_url(event["channel"])
        
        if url:
            title = self.get_title(url)
            if title:
                return title
            else:
                return "Could not find title."
        else:
            return "No URL provided."