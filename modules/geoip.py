import json
import Utils

GEOIP_URL = "http://ip-api.com/json/%s"

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("command").on("geoip"
            ).hook(self.geoip, min_args=1, help=
            "Get geoip data on a given IPv4/IPv6 address")
        #bot.events.on("received").on("command").on("geoip"
        #    ).hook(Utils.format_json, get_url_params=[
        #    GEOIP_URL
    
    def geoip(self, event):
        page = Utils.get_url(GEOIP_URL % event["args_split"][0])
        if page:
            page = json.loads(page)
        else:
            return "Failed to load results"
        if page["status"] == "success":
            data =  page["query"]
            data += " | Organisation: %s" % page["org"]
            data += " | City: %s" % page["city"]
            data += " | Region Name: %s (%s)" % (page[
                "regionName"], page["countryCode"])
            data += " | ISP: %s" % page["isp"]
            data += " | Lon/Lat %s/%s" % (page["lon"],
                page["lat"])
            data += " | Timezone: %s" % page["timezone"]
            return data
        return "No geoip data found."