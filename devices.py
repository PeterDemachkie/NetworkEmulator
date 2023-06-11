from helperfunctions import *
from network import *

class Packet:
    def __init__(self, src_addr, dst_addr, data):
        self.path = ""
        self.src_address = src_address
        self.dst_address = dst_address
        self.data = data
        self.encapsulated = False

    def getPath(self):
        return path

    def getSrc(self):
        return self.src_address

    def getDst(self):
        return self.dst_address

    def getData(self):
        return self.data

    def encapsulated(self):
        return self.encapsulated

    def encapsulate(self, src_mac, dst_mac):
        if not self.encapsulated:
            self.encapsulated = True
            frame = Frame(src_mac, dst_mac, self)
            return frame
    
    def __str__(self):
        return "SOURCE: " + self.src_address + "\nDESTINATION: " + self.dst_address + "\nDATA: " + self.data

class Frame:
    def __init__(self, src_mac, dst_mac, packet):
        self.header = None
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.packet = packet

    def getHeader(self):
        return self.header

    def getSrc(self):
        return self.src_mac

    def getDst(self):
        return self.dst_mac

    def decapsulate(self):
        self.packet.encapsulated = False
        return self.packet

class Router:
    def __init__(self, name, mac_addr):
        self.name = name
        self.mac_address = mac_addr
        self.interfaces = {} # {lan_object : device_object}
        self.routing_table = {} # {network_prefix : next_hop_ip}
        self.mac_table = {} # {mac_address : device object}
        self.ARP_cache = {} # {dst_ip : dst_mac}
        self.queue = []

    def getName(self):
        return self.name

    def getMAC(self):
        return self.mac_address

    def getInterfaces(self):
        return self.interfaces

    def getRoutes(self):
        return self.routing_table

    def getMACs(self):
        return self.mac_table

    def getARPcache(self):
        return self.ARP_cache

    def isGateway(self, lan_object):
        if lan_object.gateway is self:
            return True
        return False

    def addInterface(self, lan_object, interface_object):
        self.interfaces[lan_object] = interface_object
        self.routing_table[lan_object.network_address] = "0.0.0.0"

    def removeInterface(self, lan_object, interface_object):
        if lan_object not in self.interfaces:
            return
        # Removing the route from the routing table
        if len(self.interfaces) < 2:
            lan_object.clear_lan()
        del self.routing_table[lan_object.network_address]
           
            
    def add_mac_entry(self, mac_addr, device_obj):
        self.mac_table[mac_addr] = device_obj

    def remove_mac_entry(self, mac_addr):
        if mac_addr in self.mac_table:
            del self.mac_table[mac_addr]

    def add_route_entry(self, prefix, next_hop_ip):
        self.routing_table[prefix] = next_hop_ip

    def remove_route_entry(self, prefix, next_hop_ip):
        if prefix in self.routing_table:
            del self.routing_table[prefix]

    def update_arp_cache(self, dst_ip, dst_mac):
        if len(self.ARP_cache) >= 5:
            for entry in self.ARP_cache:
                del self.ARP_cache[entry]
                break
            self.ARP_cache[dst_ip] = dst_mac

    # Routing functionality needs work. Look at self.routing_table and the subnet_route() helperfunc
    def send_frame(self, frame):
        packet = frame.decapsulate()
        route = subnet_route(packet.dst_address, self.routing_table)
        next_hop = self.routing_table[route]
        if next_hop in self.ARP_cache:
            frame = packet.encapsulate(self.mac_address, self.ARP_cache[next_hop])
            self.mac_table[self.ARP_cache[next_hop]].recieve_frame(frame)
        else:
            #ARP Request still unfinished
            header = "ARP_REQ:" + next_hop
            for obj in self.interfaces.values():
                arp_packet = Packet(self.ip_address, next_hop, header)
                arp_frame = arp_packet.encapsulate(self.mac_address, obj.mac_address, header)
                arp_response = obj.receive_frame(arp_frame)
                if arp_respone != None:
                    self.add_mac_entry(arp_response, obj)
                    self.update_arp_cache(next_hop, arp_response)
                    frame = packet.encapsulate(self.mac_address, arp_response)
                    self.mac_table[arp_response].receive_frame(frame)
                    return
            if arp_response is None:
                print("ARP Error:", self.name, "Didnt Know What To Do With The Packet So It Threw It Away")


    def recieve_frame(self, frame):
        if frame.header[:8] == "ARP_REQ:":
            if self.ip_address == frame.header[8:]:
                return self.mac_address

        frame.packet.path += self.name + " -> "
        packet = frame.decapsulate()
        self.queue.append(packet)


class Host:
    def __init__(self, name, mac_addr, ip_addr):
        self.name = name #device name
        self.mac_address = mac_address #device mac_address
        self.ip_address = ip_address # device ip_address
        self.interface = None #Router or switch... should be set when Host is initiated
        self.routing_table = {} # {network_prefix : next_hop_ip}
        self.mac_table = {}
        self.ARP_cache = {} # {destination_ip : next_hop mac} The next hop in this case should be the hop after the switch?
        self.queue = []

    def getName(self):
        return self.name

    def getMAC(self):
        return self.mac_address

    def getInterfaces(self):
        return self.interfaces

    def getRoutes(self):
        return self.routing_table

    def getMACs(self):
        return self.mac_table

    def getARPcache(self):
        return self.ARP_cache

    def isGateway(self, lan_object):
        if lan_object.gateway is self:
            return True
        return False

    def add_table_entry(self, prefix, next_hop_ip):
        self.routing_table[prefix] = next_hop_ip

    def remove_table_entry(self, prefix, next_hop_ip):
        if self.routing_table[prefix] == next_hop_ip:
            del self.routing_table[prefix]

    def remove_interface(self):
        self.interface = None

    def send_frame(self, frame):
        packet = frame.decapsulate()
        route = subnet_route(packet.dst_address, self.routing_table) # route is set to the best match in the routing table
        next_hop = self.routing_table[route] # if the destination device is on the same LAN, next_hop is simply the destination
                                             # if not, next_hop = router_ip
        if next_hop in self.ARP_cache:
            frame = packet.encapsulate(self.mac_address, self.ARP_cache[next_hop])
            self.mac_table[next_hop].recieve_frame(frame)
        else:
            pass
            #ARP Request still unfinished
            header = "ARP_REQ:" + next_hop
            for obj in self.interfaces.values():
                arp_packet = Packet(self.ip_address, next_hop, header)
                arp_frame = arp_packet.encapsulate(self.mac_address, obj.mac_address, header)
                arp_response = obj.receive_frame(arp_frame)
                if arp_respone is not None:
                    self.add_mac_entry(arp_response, obj)
                    self.update_arp_cache(next_hop, arp_response)
                    frame = packet.encapsulate(self.mac_address, arp_response)
                    self.mac_table[arp_response].receive_frame(frame)
                    return
            if arp_response is None:
                print("ARP Error:", self.name, "Didnt Know What To Do With The Packet So It Threw It Away")


    def recieve_frame(self, frame):
        frame.packet.path += self.name
        if packet.dst_address == self.ip_address:
            self.present_packet(packet)
        else:
            frame.packet.path += " -> "
            self.send_frame(frame)


    def present_packet(self, packet):
        print(packet.path)
        print(packet.data)


class Switch:
    def __init__(self, name, mac_address):
        self.name = name
        self.mac_address = mac_address
        self.interfaces = {} # {mac_address : device_obj} 

    def getName(self):
        return self.name

    def getMAC(self):
        return self.mac_address

    def getInterfaces(self):
        return self.interfaces

    def add_interface(self, interface):
        self.interfaces[interface.mac_address] = interface

    def remove_interface(self, interface):
        if interface.mac_address not in self.mac_table:
            return
        del self.interfaces[interface.mac_address]
    
    def send_frame(self, frame):
        for mac_address in self.interfaces:
            if frame.dst_mac == mac_address:
                self.interfaces[mac_address].recieve_frame(frame)
                frame.packet.path += self.name + " -> "
                return
        print("Error:", self.name, "Didnt Know What To Do With The Packet So It Threw It Away")

    def recieve_frame(self, frame):
        frame_data = 
        if frame.decapsulate().data[:8] == "ARP_REQ:" and : # UNFINISHED <======|--0

        self.send_frame(frame)

