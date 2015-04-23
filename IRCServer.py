import re, socket, ssl
import IRCChannel, IRCChannelMode, IRCHelpers, IRCUser

RE_MODE_SYMBOLS = re.compile("PREFIX=\((\w+)\)(\W+?)(?=\s|$)", re.I)

class IRCServer(object):
    def __init__(self, config, bot):
        self.config = config
        self.bot = bot
        
        self._send_queue = []
        # underlying socket
        self._socket = socket.socket()
        # hostname to connect to
        self.server_hostname = config.get("hostname")
        # port to connect to
        self.server_port = config.get("port")
        # password to send to the server
        self.password = config.get("password")
        # whether this is an ssl connection or not
        self.ssl = config.get("ssl")
        # the address to bind onto
        self.bindhost = config.get("bindhost")
        
        # nickname, username and realname. before connecting these should be set
        # to what they're desired to be. after connecting, these will be set to
        # what the server says they are
        self.nickname = config.get("nickname")
        self.alt_nickname = config.get("alt-nickname")
        self.tried_alt = False
        self.username = config.get("username")
        self.realname = config.get("realname")
        
        # the hostname the server says we have
        self.hostname = None
        
        # list of channels we're in
        self.channels = {}
        # list of users we can see (that are in channel's we're in.)
        self.users = {}
        self.nickname_to_id = {}
        
        # all the channel mode symbols to actual modes
        self.channel_mode_symbols = {}
        
        # boolean denoting whether the server object has realised that it's been
        # disconnected or not yet connected or happily dandily connected
        self.connected = False
    
    def fileno(self):
        return self._socket.fileno()
    
    def has_handler(self, command):
        return hasattr(self, "handle_%s" % command)
    def handle_line(self, line):
        if not line:
            self.connected = False
            return None
        line_split = line.split(" ")
        if self.has_handler(line_split[1]):
            getattr(self, "handle_%s" % line_split[1])(line, line_split)
        elif not line_split[0].startswith(":") and self.has_handler(
                "%s_" % line_split[0]):
            getattr(self, "handle_%s_" % line_split[0])(line, line_split)
        return line
    
    def has_user(self, nickname):
        if nickname:
            return nickname.lower() in self.nickname_to_id
    def get_user_by_nickname(self, nickname):
        if nickname:
            return self.users.get(self.nickname_to_id.get(nickname.lower(),
                None), None)
    def add_user(self, nickname):
        if not self.has_user(nickname):
            IRCUser.IRCUser(nickname, self)
            self.bot.events.on("new").on("user").call(
                user=self.get_user_by_nickname(nickname), server=self)
    def remove_user(self, nickname):
        user = self.get_user_by_nickname(nickname)
        if user:
            user.destroy()
    
    def check_users(self):
        for user in list(self.users.values()):
            if len(user.channels) == 0:
                user.destroy()
    
    def has_channel(self, channel_name):
        return channel_name.lower() in self.channels
    def get_channel(self, channel_name):
        return self.channels.get(channel_name.lower(), None)
    def add_channel(self, channel_name):
        if not self.has_channel(channel_name):
            self.channels[channel_name.lower()] = IRCChannel.IRCChannel(
                channel_name, self, self.config.get("channels", {}).get(
                channel_name, {}))
            self.bot.events.on("new").on("channel").call(
                channel=self.get_channel(channel_name), server=self)
    
    def connect(self):
        assert self.server_hostname
        assert self.server_port
        assert self.nickname
        self.username = self.username or self.nickname
        self.realname = self.realname or self.nickname
        self._socket = socket.socket()
        try:
            self._socket.connect((self.server_hostname, self.server_port))
        except Exception as e:
            raise e
        try:
            if self.ssl:
                self._socket = ssl.wrap_socket(self._socket)
        except Exception as e:
            raise e
        self.send_pass(self.password)
        self.send_user(self.username, self.realname)
        self.send_nick(self.nickname)
        self.connected = True
    
    def disconnect(self):
        self.send_quit()
        self.connected = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
    
    def read_line(self):
        line = b""
        while True:
            try:
                byte = self._socket.recv(1)
            except:
                return None
            if byte == b"\n":
                break
            elif byte == b"\r":
                continue
            line += byte
        try:
            line = line.decode(self.config.get("encoding", "utf8"))
        except UnicodeDecodeError as e:
            line = line.decode(
                self.config.get("fallback-encoding", "iso-8859-1"))
        if line:
            return self.handle_line(line)
        return None
    
    def waiting_send(self):
        return len(self._send_queue) > 0
    def send_line(self):
        try:
            line = self._send_queue.pop(0).encode("utf8")
            self._socket.send(line)
        except Exception as e:
            raise e
    def queue_line(self, line):
        self._send_queue.append("%s\r\n" % line)
    def send_pass(self, password):
        if password:
            self.queue_line("PASS %s" % password)
    def send_user(self, username, realname):
        if username and realname:
            self.queue_line("USER %s - - :%s" % (username, realname))
    def send_nick(self, nickname):
        if nickname:
            self.queue_line("NICK %s" % nickname)
    def send_whois(self, nickname):
        if nickname:
            self.queue_line("WHOIS %s" % nickname)
    def send_who(self, argument):
        if argument:
            self.queue_line("WHO %s" % argument)
    def send_join(self, channel_name):
        if channel_name:
            self.queue_line("JOIN %s" % channel_name)
    def send_ping(self, nonce):
        if nonce:
            self.queue_line("PING :%s" % nonce)
    def send_pong(self, nonce):
        if nonce:
            self.queue_line("PONG :%s" % nonce)
    def send_quit(self, message=None):
        message = message or self.config.get("quit-message", "Leaving")
        self.queue_line("QUIT :%s" % message)
    def send_message(self, recipient, text):
        if recipient and text:
            channel = self.get_channel(recipient)
            user = self.get_user_by_nickname(recipient)
            sub_event = None
            if channel:
                sub_event = "channel"
            elif user:
                sub_event = "private"
            self.queue_line("PRIVMSG %s :%s" % (recipient, text))
            if sub_event:
                self.bot.events.on("send").on("message").on(
                    sub_event).call(text=text, user=user, channel=channel,
                    sender=self.get_user_by_nickname(self.nickname),
                    action=False, server=self)
    def send_action(self, recipient, text):
        if recipient and text:
            channel = self.get_channel(recipient)
            user = self.get_user_by_nickname(recipient)
            sub_event = None
            if channel:
                sub_event = "channel"
            elif user:
                sub_event = "private"
            self.queue_line("PRIVMSG %s :\01ACTION %s\01" % (
                recipient, text))
            if sub_event:
                self.bot.events.on("send").on("message").on(
                    sub_event).call(text=text, user=user, channel=channel,
                    sender=self.get_user_by_nickname(self.nickname),
                    action=True, server=self)
    
    def get_own_hostmask(self):
        return "%s!%s@%s" % (nickname, username, hostname)
    def own_nickname(self, nickname):
        return nickname.lower() == self.nickname.lower()
    
    def handle_JOIN(self, line, line_split):
        nickname, username, hostname = IRCHelpers.hostmask_split(line_split[0])
        channel_name = IRCHelpers.remove_colon(
            IRCHelpers.get_index(line_split, 2))
        if self.own_nickname(nickname):
            self.add_channel(channel_name)
            self.get_channel(channel_name).send_who()
            self.bot.events.on("self").on("join").call(line=line,
                line_split=line_split, server=self,
                channel=self.get_channel(channel_name))
        else:
            if not self.has_user(nickname):
                self.add_user(nickname)
            self.bot.events.on("received").on("join").call(line=line,
                line_split=line_split, server=self,
                channel=self.get_channel(channel_name),
                user=self.get_user_by_nickname(nickname))
    def handle_PART(self, line, line_split):
        nickname, username, hostname = IRCHelpers.hostmask_split(line_split[0])
        if self.own_nickname(nickname):
            self.part_channel(IRCHelpers.get_index(line_split, 2))
    def handle_QUIT(self, line, line_split):
        nickname, username, hostname = IRCHelpers.hostmask_split(line_split[0])
        user = self.get_user_by_nickname(nickname)
        if user:
            user.destroy()
    def handle_MODE(self, line, line_split):
        nickname, username, hostname = IRCHelpers.hostmask_split(line_split[0])
        modes = IRCHelpers.remove_colon(IRCHelpers.get_index(line_split, 3) or
            "")
        arguments = line_split[4:]
        mode_count = (len(modes) - modes.count("+")) - modes.count("-")
        recipient_name = IRCHelpers.get_index(line_split, 2)
        channel = self.get_channel(recipient_name)
        user = self.get_user_by_nickname(recipient_name)
        recipient = channel or user
        
        if recipient:
            current_index = 0
            add_mode = True
            for char in modes:
                if char == "+":
                    add_mode = True
                elif char == "-":
                    add_mode = False
                else:
                    argument = None
                    if mode_count - current_index == len(arguments):
                        argument = arguments.pop(0)
                    if add_mode:
                        recipient.add_mode(char, argument)
                    else:
                        recipient.remove_mode(char, argument)
                    current_index += 1
    def handle_NICK(self, line, line_split):
        nickname, username, hostname = IRCHelpers.hostmask_split(line_split[0])
        new_nick = IRCHelpers.get_index(line_split, 2)
        if self.own_nickname(nickname):
            self.nickname = new_nick
        else:
            user = self.get_user_by_nickname(nickname)
            if user:
                user.change_nickname(new_nick)
    def handle_PRIVMSG(self, line, line_split):
        nickname, username, hostname = IRCHelpers.hostmask_split(line_split[0])
        sender = self.get_user_by_nickname(nickname)
        recipient_name = IRCHelpers.get_index(line_split, 2)
        channel = self.get_channel(recipient_name)
        user = self.get_user_by_nickname(recipient_name)
        action = False
        text = IRCHelpers.arbitrary(line_split[3:])
        if text.startswith("\01ACTION ") and text.endswith("\01"):
            action = True
            text = text.replace("\01ACTION ", "", 1)[-1]
        text_split = text.split()
        if channel:
            self.bot.events.on("received").on("message").on("channel").call(
                line=line, line_split=line_split, server=self, channel=channel,
                text=text, text_split=text_split, sender=sender, action=action)
        elif user:
            self.bot.events.on("received").on("message").on("private").call(
                line=line, line_split=line_split, server=self, text=text,
                text_split=text_split, sender=sender, action=action)
    def handle_001(self, line, line_split):
        self.nickname = IRCHelpers.get_index(line_split, 2)
        self.send_whois(self.nickname)
        self.bot.events.on("received").on("numeric").on("001").call(line=line,
            line_split=line_split, server=self)
    # response to whois
    def handle_311(self, line, line_split):
        nickname = IRCHelpers.get_index(line_split, 2)
        if self.own_nickname(nickname):
            self.username = IRCHelpers.get_index(line_split, 4)
            self.hostname = IRCHelpers.get_index(line_split, 5)
            self.realname = IRCHelpers.arbitrary(line_split[7:])
    # response to WHO
    def handle_352(self, line, line_split):
        channel = self.get_channel(IRCHelpers.get_index(line_split, 3))
        nickname = IRCHelpers.get_index(line_split, 7)
        self.add_user(nickname)
        user = self.get_user_by_nickname(nickname)
        if user:
            username = IRCHelpers.get_index(line_split, 4)
            hostname = IRCHelpers.get_index(line_split, 5)
            realname = IRCHelpers.arbitrary(line_split[10:])
            if username:
                user.username = username
            if hostname:
                user.hostname = hostname
            if realname:
                user.realname = realname
            user.join_channel(channel)
    def handle_PING_(self, line, line_split):
        nonce = IRCHelpers.arbitrary(line_split[1:])
        self.send_pong(nonce)
    # nickname taken
    def handle_433(self, line, line_split):
        if not self.tried_alt and self.alt_nickname:
            self.send_nick(self.alt_nickname)
    # extra capabilities
    def handle_005(self, line, line_split):
        match = re.search(RE_MODE_SYMBOLS, line)
        if match and len(match.group(1)) == len(match.group(2)):
            for n, symbol in enumerate(match.group(2)):
                self.channel_mode_symbols[symbol] = match.group(1)
    # userlist on channel join
    def handle_353(self, line, line_split):
        nicknames = line_split[5:]
        if nicknames and nicknames[0].startswith(":"):
            nicknames[0] = nicknames[0][1:]
        channel = self.get_channel(IRCHelpers.get_index(line_split, 4))
        for nickname in nicknames:
            for char in nickname:
                if char in self.channel_mode_symbols:
                    # make mark down the mode
                    nickname = nickname[1:]
            self.add_user(nickname)
            self.get_user_by_nickname(nickname).join_channel(channel)