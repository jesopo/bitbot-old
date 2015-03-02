import socket, ssl
import IRCHelpers

class IRCServer(object):
    def __init__(self):
        self._send_queue = []
        # underlying socket
        self._socket = None
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
        
        self.connected = False
    
    def has_handler(self, command):
        return hasattr(self, "handle_%s" % command)
    def handle_line(self, line):
        line_split = line.split(" ")
        if self.has_handler(line_split[1]):
            getattr(self, "handle_%s" line_split[1])(line, line_split)
    
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
        if self.password:
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
        self.handle_line(line)
        return line
    
    def send_line(self, line):
        self._send_queue.append("%s\r\n" % line.encode("utf8"))
    def send_pass(self, password):
        self.send_line("PASS %s" % password)
    def send_user(self, username, realname):
        self.send_line("USER %s - - :%s" % (username, realname))
    def send_nick(self, nickname):
        self.send_line("NICK %s" % nickname)
    def send_whois(self, nickname):
        self.send_line("WHOIS %s" % nickname)
    
    def handle_001(self, line, line_split):
        self.nickname = line_split[2]
        self.send_whois(self.nickname)
    def handle_311(self, line, line_split):
        nickname = line_split[2]
        if nickname == self.nickname:
            self.username = line_split[4]
            self.hostname = line_split[5]
            self.realname = IRCHelpers.arbitrary(line_split[7:])