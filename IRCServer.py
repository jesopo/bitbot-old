import socket, ssl
import IRCChannel, IRCChannelMode, IRCHelpers, IRCUser

class IRCServer(object):
    def __init__(self, config):
        self.config = config
        
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
        self.username = config.get("username")
        self.realname = config.get("realname")
        
        # the hostname the server says we have
        self.hostname = None
        
        # list of channels we're in
        self.channels = {}
        # list of users we can see (that are in channel's we're in.)
        self.users = {}
        self.nickname_to_id = {}
        
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
        return line
    
    def has_user(self, nickname):
        if nickname:
            return nickname.lower() in self.nickname_to_id
    def get_user_by_nickname(self, nickname):
        if nickname:
            return self.users.get(self.nickname_to_id.get(nickname.lower(),
                None), None)
    def add_user(self, nickname):
        IRCUser.IRCUser(nickname, self)
    
    def has_channel(self, channel_name):
        return channel_name.lower() in self.channels
    def get_channel(self, channel_name):
        return self.channels.get(channel_name.lower(), None)
    
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
    
    def read_line(self):
        line = ""
        while True:
            byte = self._socket.recv(1).decode("utf8")
            if byte == "\n":
                break
            line += byte
        line = line.strip("\r")
        return self.handle_line(line)
    
    def waiting_send(self):
        return len(self._send_queue) > 0
    def send_line(self):
        try:
            self._socket.send(self._send_queue.pop(0).encode("utf8"))
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
        
    
    def get_own_hostmask(self):
        return "%s!%s@%s" % (nickname, username, hostname)
    def own_nickname(self, nickname):
        return nickname.lower() == self.nickname.lower()
    
    def handle_JOIN(self, line, line_split):
        nickname, username, hostname = IRCHelpers.hostmask_split(line_split[0])
        channel_name = IRCHelpers.get_index(line_split, 2)
        if self.own_nickname(nickname):
            if not channel_name.lower() in self.channels:
                self.channels[channel_name.lower()] = IRCChannel.IRCChannel(
                    channel_name, self)
            self.get_channel(IRCHelpers.get_index(line_split, 2)).send_who()
        else:
            if not self.has_user(nickname):
                self.add_user(nickname)
                
                
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
    def handle_001(self, line, line_split):
        self.nickname = IRCHelpers.get_index(line_split, 2)
        self.send_whois(self.nickname)
        self.send_join("#schoentoon")
    def handle_311(self, line, line_split):
        nickname = IRCHelpers.get_index(line_split, 2)
        if self.own_nickname(nickname):
            self.username = IRCHelpers.get_index(line_split, 4)
            self.hostname = IRCHelpers.get_index(line_split, 5)
            self.realname = IRCHelpers.arbitrary(line_split[7:])
    def handle_525(self, line, line_split):
        user = self.get_user_by_nickname(IRCHelpers.get_index(line_split, 7))
        if user:
            username = IRCHelpers.get_index(line_split, 4)
            hostname = IRCHelpers.get_index(line_split, 5)
            if username:
                user.username = username
            if hostname:
                user.hostname = hostname
        