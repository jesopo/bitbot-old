import json
import Utils

SPOTIFY_URL = "https://api.spotify.com/v1/search"

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("command").on("spotify").hook(
            self.spotify, help="Search for a track on spotify",
            min_args=1)
    
    def spotify(self, event):
        search_term = event["args"]
        page = Utils.get_url(SPOTIFY_URL, get_params={"type": "track",
            "limit": 1, "q": search_term})
        if page:
            page = json.loads(page)
        else:
            return "Failed to load results"
        if len(page["tracks"]["items"]):
            item = page["tracks"]["items"][0]
            title = item["name"]
            artist_name = item["artists"][0]["name"]
            url = item["external_urls"]["spotify"]
            return "%s (by %s) %s" % (title, artist_name, url)
        return "No results found"