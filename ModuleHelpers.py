import re, traceback, urllib.parse, urllib.request

RE_CHARSET = re.compile("charset=(\S+)", re.I)
REGEX_MAX_LENGTH = re.compile(".{1,300}(?=\s|$)")

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
    match = re.search(RE_CHARSET, encoding)
    if match:
        encoding = match.group(1)
    else:
        encoding = "utf8"
    
    return response.read().decode(encoding)
