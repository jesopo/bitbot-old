import datetime, re
from twitter import OAuth, Twitter

REGEX_TWITTER_URL = re.compile("https?://twitter.com/[^/]+/status/(\d+)")

class Module(object):
    _name = "Twitter"
    def __init__(self, bot):
        self.bot = bot
        bot.events.on("received").on("command").on("twitter"
            ).hook(self.twitter)
        bot.events.on("received").on("command").on("tw"
            ).hook(self.twitter)
    
    def url_from_log(self, channel):
        for log in channel.log:
            tweet_id = self.tweet_id(log.text)
            if tweet_id:
                return tweet_id
    
    def tweet_id(self, text):
        match = re.search(REGEX_TWITTER_URL, text)
        if match:
            return match.group(1)
    
    def make_timestamp(self, s):
        timestamp = datetime.datetime.strptime(s, "%a %b %d %H:%M:%S +0000 %Y")
        return timestamp.strftime("%H:%M:%S %d/%m/%Y")
    
    def twitter(self, event):
        oauth_token = self.bot.config.get("twitter-oauth-token")
        oauth_token_secret = self.bot.config.get(
            "twitter-oauth-token-secret")
        consumer_key = self.bot.config.get("twitter-consumer-key")
        consumer_secret = self.bot.config.get("twitter-consumer-secret")
        
        arg = ""
        if event["args_split"]:
            arg = event["args_split"][0]
        
        if oauth_token and oauth_token_secret and consumer_key and consumer_secret:
            twitter = Twitter(auth=OAuth(oauth_token, oauth_token_secret,
                consumer_key, consumer_secret))
            if arg.startswith("@"):
                tweets = twitter.statuses.user_timeline(screen_name=arg[1:],
                    count=1)
                if tweets:
                    screen_name = "@%s" % tweets[0]["user"]["screen_name"]
                    if tweets[0]["retweeted"]:
                        original_screen_name = "@%s" %tweets[0]["retweeted_status"
                            ]["user"]["screen_name"]
                        original_text = tweets[0]["retweeted_status"]["text"]
                        return "(%s retweeted %s at %s) %s" % (screen_name,
                            original_screen_name, self.make_timestamp(tweets[0][
                            "retweeted_status"]["created_at"]), original_text)
                    return "(%s at %s) %s" % (screen_name, self.make_timestamp(
                        tweets[0]["created_at"]), tweets[0]["text"])
            tweet_id = None
            if arg.isdigit():
                tweet_id = arg
            else:
                if arg:
                    tweet_id = self.tweet_id(arg)
                else:
                    tweet_id = self.url_from_log(event["channel"])
            if tweet_id:
                tweet = twitter.statuses.show(id=tweet_id)
                if tweet:
                    return "(@%s at %s) %s" % (tweet["user"]["screen_name"],
                        self.make_timestamp(tweet["created_at"]), tweet["text"])
                return "failed to get tweet."
            else:
                return "no tweet to get."