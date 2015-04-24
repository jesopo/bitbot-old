import re, traceback, urllib.parse, urllib.request

REGEX_HOSTMASK = re.compile(":?([^!]*)!([^@]*)@(.*)")
REGEX_CHARSET = re.compile("charset=(\S+)", re.I)
REGEX_MAX_LENGTH = re.compile(".{1,300}(?=\s|$)")

# get a webpage, try to decode it by encoding specified in headers or utf8
def get_url(url, **get_params):
    data = ""
    if get_params:
        data = "%s" % urllib.parse.urlencode(get_params)
    url = "%s?%s" % (url, data)
    try:
        response = urllib.request.urlopen(url)
    except:
        traceback.print_exc()
        return None
    encoding = response.info().get("content-type", "")
    match = re.search(REGEX_CHARSET, encoding)
    if match:
        encoding = match.group(1)
    else:
        encoding = "utf8"
    
    return response.read().decode(encoding)

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