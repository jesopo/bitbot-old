import socket, ssl
import IRCChannel, IRCChannelMode, IRCHelpers, IRCUser

class IRCServer(object):
    def __init__(self):
        self._send_queue = []
        # underlying socket
        self._socket = socket.socket()
        # hostname to connect to
        self.server_hostname = None
        # port to connect to
        self.server_port = None
        # password to send to the server
        self.password = None
        # whether this is an ssl connection or not
        self.ssl = None
        # the address to bind onto
        self.bindhost = None
        
        # nickname, username and realname. before connecting these should be set
        # to what they're desired to be. after connecting, these will be set to
        # what the server says they are
        self.nickname = None
        self.username = None
        self.realname = None
        
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
        return nickname.lower() in self.nickname_to_id
    def get_user_by_nickname(self, nickname):
        return self.users.get(self.nickname_to_id.get(nickname.lower(), None),
            None)
    
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
    
    def readline(self):
        line = ""
        while True:
            byte = self._socket.recv(1)
            if byte == "\n":
                break
            line += byte
        line = line.strip("\r").decode("utf8")
        return self.handle_line(line)
    
    def waiting_send(self):
        return len(self._send_queue) > 0
    def send_line(self):
        try:
            self._socket.send(self._send_queue.pop(0))
        except Exception as e:
            raise e
    def queue_line(self, line):
        self._send_queue.append("%s\r\n" % line.encode("utf8"))
    def send_pass(self, password):
        if password:
            self.queue_line("PASS %s" % password)
    def send_user(self, username, realname):
        if nickname and realname:
            self.queue_line("USER %s - - :%s" % (username, realname))
    def send_nick(self, nickname):
        if nickname:
            self.queue_line("NICK %s" % nickname)
    def send_whois(self, nickname):
        if nickname:
            self.queue_line("WHOIS %s" % nickname)
    
    def join_channel(self, channel_name):
        if not channel_name.lower() in self.channels:
            self.channels
    
    def get_own_hostmask(self):
        return "%s!%s@%s" % (nickname, username, hostname)
    def own_nickname(self, nickname):
        return nickname.lower() == self.nickname.lower()
    
    def handle_JOIN(self, line, line_split):
        nickname, username, hostname = IRCHelpers.hostmask_split(line_split[0])
        if self.own_nickname(nickname):
            self.join_channel(IRCHelpers.get_index(line_split, 2))
    def handle_PART(self, line, line_split):
        nickname, username, hostname = IRCHelpers.hostmask_split(line_split[0])
        if self.own_nickname(nickname):
            self.part_channel(IRCHelpers.get_index(line_split, 2))
    def handle_001(self, line, line_split):
        self.nickname = IRCHelpers.get_index(line_split, 2)
        self.send_whois(self.nickname)
    def handle_311(self, line, line_split):
        nickname = IRCHelpers.get_index(line_split, 2)
        if self.own_nickname(nickname):
            self.username = IRCHelpers.get_index(line_split, 4)
            self.hostname = IRCHelpers.get_index(line_split, 5)
            self.realname = IRCHelpers.arbitrary(line_split[7:])