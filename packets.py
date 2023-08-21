# Peter Demachkie
# packets.py
# www.github.com/PeterDemachkie/NetworkEmulator
# peterdemachkie101@gmail.com
class UDP:
    def __init__(self, src_ip, dest_ip, data = None):
        self.data = data
        self.src_ip = src_ip
        self.dest_ip = dest_ip

    def get_src_ip(self):
        return self.src_ip

    def get_dest_ip(self):
        return self.dest_ip

    def get_data_ip(self):
        return self.data
    

class ARP:
    def __init__(self, src_ip, src_mac, dest_ip, dest_mac = None, device_object = None):
        self.request = not bool(dest_mac)
        self.src_mac = src_mac
        self.src_ip = src_ip
        self.dest_mac = dest_mac
        self.dest_ip = dest_ip
        self.device_object = device_object

    def is_request(self):
        return self.request

    def get_src_mac(self):
        return self.src_mac

    def get_src_ip(self):
        return self.src_ip

    def get_dest_mac(self):
        return self.dest_mac

    def get_dest_ip(self):
        return self.dest_ip

    def get_device_object(self):
        return self.object

    "NEED A WAY TO SEND DEVICE OBJECT IN ARP RESPONSE"


class ICMP:
    def __init__(self, src_ip, dest_ip, time, request=False):
        self.time = time
        self.request = request
        self.src_ip = src_ip
        self.dest_ip = dest_ip

    def get_time(self):
        return self.time

    def is_request(self):
        return self.request

    def get_src_ip(self):
        return self.src_ip

    def get_dest_ip(self):
        return self.src_ip


class Frame:
    def __init__(self, src_mac, dest_mac, src_object, packet):
        self.src_mac = src_mac
        self.dest_mac = dest_mac
        self.src_object = src_object
        self.packet = packet
    
    def get_src_mac(self):
        return self.src_mac

    def get_dest_mac(self):
        return self.dest_mac

    def get_src_object(self):
        return self.src_object

    def decapsulate(self):
        return self.packet