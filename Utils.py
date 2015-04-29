import html.parser, re, traceback, urllib.parse, urllib.request

REGEX_HOSTMASK = re.compile(":?([^!]*)!([^@]*)@(.*)")
REGEX_CHARSET = re.compile("charset=(\S+)", re.I)
REGEX_MAX_LENGTH = re.compile(".{1,300}(?=\s|$)")

h = html.parser.HTMLParser()

# get a webpage, try to decode it by encoding specified in headers or utf8
def get_url(url, **kwargs):
    method = kwargs.get("method", "GET")
    get_params = kwargs.get("get_params", "")
    post_params = kwargs.get("post_params", None)
    data = ""
    if get_params:
        get_params = urllib.parse.urlencode(get_params)
    if post_params:
        post_params = urllib.parse.urlencode(post_params).encode("utf8")
    url = "%s?%s" % (url, get_params)
    request = urllib.request.Request(url, post_params)
    request.add_header("Accept-Language", "en-gb")
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