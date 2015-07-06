import glob, html.parser, os, re, traceback, urllib.parse, urllib.request

REGEX_HOSTMASK = re.compile(":?([^!]*)!([^@]*)@(.*)")
REGEX_CHARSET = re.compile("charset=(\S+)", re.I)
REGEX_MAX_LENGTH = re.compile(".{1,300}(?:\s|$)")

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 " \
    "(KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36"

TIME_SECOND = 1
TIME_MINUTE = TIME_SECOND*60
TIME_HOUR = TIME_MINUTE*60
TIME_DAY = TIME_HOUR*24
TIME_WEEK = TIME_DAY*7

current_directory = os.path.dirname(os.path.abspath(__file__))

h = html.parser.HTMLParser()

# get a webpage, try to decode it by encoding specified in headers or utf8
def get_url(url, **kwargs):
    method = kwargs.get("method", "GET")
    get_params = kwargs.get("get_params", "")
    post_params = kwargs.get("post_params", None)
    data = ""
    if get_params:
        get_params = "?%s" % urllib.parse.urlencode(get_params)
    if post_params:
        post_params = urllib.parse.urlencode(post_params).encode("utf8")
    url = "%s%s" % (url, get_params)
    request = urllib.request.Request(url, post_params)
    request.add_header("Accept-Language", "en-gb")
    request.add_header("User-Agent", USER_AGENT)
    request.method = method
    try:
        response = urllib.request.urlopen(request)
    except:
        traceback.print_exc()
        return None
    encoding = response.info().get_content_charset() or "utf8"
    
    return response.read().decode(encoding)

# parse html entities
def html_entities(text):
    return h.unescape(text)

# remove the colon from a start of the string, if there is one there
def remove_colon(s):
    return s if not s.startswith(":") else s[1:]

# combine an arbitrarily long array into a string, assume that it's IRC's style
# of arbitrarily long, ergo prefixed with a colon
def arbitrary(words):
    return remove_colon(" ".join(words))

# split up a nickname!username@hostname combo into the relevant parts
def hostmask_split(hostmask):
    hostmask_match = re.match(REGEX_HOSTMASK, hostmask)
    if not hostmask_match:
        return [None, None, None]
    return hostmask_match.groups()

# try to get the word at position i, if not, return null
def get_index(words, i):
    try:
        return words[i]
    except IndexError:
        return None

def overflow_truncate(text):
    return re.match(REGEX_MAX_LENGTH, text).group(0)

def certificates():
    return glob.glob(os.path.join(current_directory, "certs", "*.crt"))

def time_unit(seconds):
    since = None
    unit = None
    if seconds >= TIME_WEEK:
        since = seconds/TIME_WEEK
        unit = "week"
    elif seconds >= TIME_DAY:
        since = seconds/TIME_DAY
        unit = "day"
    elif seconds >= TIME_HOUR:
        since = seconds/TIME_HOUR
        unit = "hour"
    elif seconds >= TIME_MINUTE:
        since = seconds/TIME_MINUTE
        unit = "minute"
    else:
        since = seconds
        unit = "second"
    since = int(since)
    if since > 1:
        unit = "%ss" % unit # pluralise the unit
    return [since, unit]