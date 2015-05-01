import re

REGEX_SPLIT = re.compile("(?<!\\\\)/")

class Module(object):
    def __init__(self, bot):
        bot.events.on("received").on("message").on("channel").hook(self.message)
    
    def message(self, event):
        if not hasattr(event["channel"], "log"):
            return
        sed_split = re.split(REGEX_SPLIT, event["text"], 3)
        if event["text"].startswith("s/") and len(sed_split) > 2:
            count = ""
            last_flag = ""
            flags = ""
            if len(sed_split) == 4:
                flags = sed_split[3].lower()
            re_flags = 0
            for flag in flags:
                if flag.isdigit() and (last_flag.isdigit() or not count):
                    count += flag
                elif flag == "i":
                    re_flags |= re.I
                elif flag == "g":
                    count = "0"
                last_flag = flag
            if count:
                count = int(count)
            else:
                count = 1
            
            pattern = re.compile(sed_split[1], re_flags)
            replace = sed_split[2].replace("\\/", "/")
            
            for log in event["channel"].log:
                if log.text.startswith("s/") or log.from_self:
                    continue
                match = re.search(pattern, log.text)
                if match:
                    new_message = re.sub(pattern, replace, log.text, count)
                    if not log.is_action:
                        event["channel"].send_message("<%s> %s" % (
                            log.nickname, new_message))
                    else:
                        event["channel"].send_message("* %s %s" % (
                            log.nickname, new_message))
                    break
