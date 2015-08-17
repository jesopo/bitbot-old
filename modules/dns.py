import socket

class Module(object):
    _name = "DNS"
    def __init__(self, bot):
        bot.events.on("received").on("command").on("dns"
            ).hook(self.dns, min_args=1,
            help="Get all IPs related to a hostname (IPv4/IPv6)")
    
    def dns(self, event):
        try:
            addresses = socket.getaddrinfo(event["args_split"][0],
                80, 0, socket.SOCK_DGRAM)
        except socket.gaierror:
            return "Unknown hostname"
        ips = []
        for _, _, _, _, address in addresses:
            ips.append(address[0])
        return "%s: %s" % (event["args_split"][0], ", ".join(ips))