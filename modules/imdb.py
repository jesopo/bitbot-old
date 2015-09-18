import json
import Utils

OMDB_URL = "http://www.omdbapi.com/"

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("command").on("imdb"
            ).hook(self.imdb, min_args=1,
            help="Get data on a given media title.")
    
    def imdb(self, event):
        page = Utils.get_url(OMDB_URL, get_params={
            "t": event["args"]})
        if page:
            page = json.loads(page)
        else:
            return "Failed to load results"
        if "Title" in page:
            return ["IMDb", "%s, %s (%s) %s (%s/10.0)" % (
                page["Title"], page["Year"], page["Runtime"
                ], page["Plot"], page["imdbRating"])]
        return "Title not found"