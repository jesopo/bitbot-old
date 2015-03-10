import re

# remove the colon from a start of the string, if there is one there
def remove_colon(s):
    return s if not s.startswith(":") else s[1:]

# combine an arbitrarily long array into a string, assume that it's IRC's style
# of arbitrarily long, ergo prefixed with a colon
def arbitrary(words):
    return remove_colon(" ".join(words))

RE_HOSTMASK = re.compile("([^!]*)!([^@]*)@(.*)")
# split up a nickname!username@hostname combo into the relevant parts
def hostmask_split(hostmask):
    hostmask_match = re.match(RE_HOSTMASK, remove_colon(hostmask))
    if not hostmask_match:
        return [None, None, None]
    return hostmask_match.groups()

# try to get the word at position i, if not, return null
def get_index(words, i):
    try:
        return words[i]
    except IndexError:
        return None