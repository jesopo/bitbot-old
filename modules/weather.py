import json
import Utils

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("command").on("weather").hook(
            self.weather, min_args=1, help="Get the weather for a "
            "given location")
    
    def weather(self, event):
        page = Utils.get_url(WEATHER_URL, get_params={"q":
            event["args"], "units": "metric"})
        if page:
            page = json.loads(page)
        else:
            return "Failed to load results"
        if "weather" in page:
            location = "%s, %s" % (page["name"], page["sys"][
                "country"])
            celsius = "%dC" % page["main"]["temp"]
            fahrenheit = "%dF" % ((page["main"]["temp"]*9/5)+32)
            description = page["weather"][0]["description"].title()
            humidity = "%s%%" % page["main"]["humidity"]
            wind_speed = "%sKM/H" % page["wind"]["speed"]
            
            return "(%s) %s/%s | %s | Humidity: %s | Wind: %s" % (
                location, celsius, fahrenheit, description, humidity,
                wind_speed)
        return "No weather for this location"