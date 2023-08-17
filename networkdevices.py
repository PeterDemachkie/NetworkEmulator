# Peter Demachkie
# networkdevices.py
# www.github.com/PeterDemachkie/NetworkEmulator
# peterdemachkie101@gmail.com

import packets
import ipaddress
import time

class Router:
    def __init__(self, name, mac_address, controller):
        self.controller = controller
        self.name = name
        self.mac_address = mac_address
        self.routing_table = {"0.0.0.0/0" : None}# {network : next_hop_ip} ?
        self.arp_table = {} # {ip_address : [mac_address, device object, timer]}
        self.address_table = {} # {router_ip : network}

    #ACCESS FUNCTIONS
    def get_name(self):
        return self.name

    def get_mac(self):
        return self.mac_address

    def get_ip_address(self, network):
        for router_ip, network_address in self.address_table.items():
            if network_address == network:
                return router_ip

    def get_networks(self):
        return self.address_table.values()

    def get_source_ip(self, dest_ip):
        next_hop = self.get_next_hop(dest_ip)
        net = None
        for network, hop in self.routing_table.items():
            if hop == next_hop:
                net = network
        for address, network in self.address_table.items():
            if network == net:
                return address
            
    def get_next_hop(self, dest_ip):
        largest_subst = ""
        for addr in self.routing_table:
            if ip_to_bin(addr) in ip_to_bin(dest_ip) and len(ip_to_bin(addr)) > len(ip_to_bin(largest_subst)):
                largest_subst = addr
        if largest_subst == "0.0.0.0/0":
            return None
        return self.routing_table[largest_subst]
        "MAKE SURE THAT THIS CONCEPT ACTUALLY WORKS"
        "I think it does, if anythings wrong im gonna find it in test"

    # SET/ADD ENTRY FUNCTIONS
    def set_name(self, name):
        self.name = name

    def add_route(self, dest_network, next_hop):
        self.routing_table[dest_network] = next_hop

    def add_network(self, router_ip, network_address):
        self.address_table[router_ip] = network_address

    # REMOVE/CLEAR FUNCTIONS
    def remove_route(self, dest_network):
        del self.routing_table[dest_network]
    
    def remove_network(self, network_address):
        for router_ip, network in self.address_table.items():
            if network == network_address:
                del self.address_table[router_ip]

    def clear_routing_table(self):
        for network in self.routing_table:
            self.remove_route(network)

    # PROCESS FUNCTIONS
    def forward_packet(self, packet):
        next_hop = self.get_next_hop(packet.get_dest_ip())
        if next_hop in self.arp_table:
            frame = Frame(self.mac_address, self.arp_table[next_hop][0], packet, self)
            next_hop_device = self.arp_table[next_hop][1]
            next_hop_device.handle_incoming_frame(frame)
        else:
            return False

    def generate_udp_packet(self, dest_ip, data = None):
        source = self.get_source_ip(dest_ip)
        udp_packet = packets.UDP(source, dest_ip, data)
        return udp_packet

    def handle_udp_packet(self, udp_packet):
        if udp_packet.get_dest_ip() in self.address_table:
            data = udp_packet.get_data()
            if data is not None:
                if data[:12] == "DHCP_UPDATE: ":
                    self.update_routing_table(udp_packet.get_src_ip(), data)
                else:
                    self.controller.listen(self.name, data)
        else:
            self.forward_packet(udp_packet)

    def generate_arp_request(self, dest_ip):
        source = self.get_source_ip(dest_ip)
        arp_packet = ARP(source, dest_ip, self.mac_address)
        return arp_packet

    def handle_arp_packet(self, arp_packet):
        if arp_packet.request:
            if arp_packet.get_dest_ip() in self.address_table:
                response_packet = packets.ARP(arp_packet.get_dest_ip(), self.mac, arp_packet.get_src_ip(), dest_mac=arp_packet.src_mac, device_object = self)
                self.forward_packet(response_packet)
                self.update_arp_table(arp_packet)
        else:
            self.update_arp_table(arp_packet)

    def generate_icmp_request(self, dest_ip):
        source = self.get_source_ip(dest_ip)
        icmp_packet = packets.ICMP(source, dest_ip, time.time(), request=True)
        return icmp_packet

    def handle_icmp_packet(self, icmp_packet):
        if icmp_packet.request: 
            if icmp_packet.get_dest_ip() in self.address_table:
                response_packet = packets.ICMP(icmp_packet.get_dest_ip(), icmp_packet.get_src_ip(), icmp_packet.get_time())
                self.forward_packet(response_packet)
            else:
                if self.get_next_hop(icmp_packet.get_dest_ip()) is None:
                    response_packet = packets.ICMP(icmp_packet.get_src_ip(), icmp_packet.get_src_ip(), None)
                    self.forward_packet(response_packet)
                else:
                    self.forward_packet(icmp_packet)
        else:
            if icmp_packet.get_time() is None:
                return "Error: Host " + icmp_packet.get_src_ip() + " Unreachable."
            else:
                rtt = icmp_packet.get_time() - time.time()
                return str(icmp_packet.get_src_ip()) + " is live. RTT: " + str(round(rtt, 2))
        
            
    def handle_incoming_frame(self, frame):
        packet = frame.decapsulate()
        if isinstance(packet, packets.UDP):
            self.handle_udp_packet(packet)
        if isinstance(packet, packets.ARP):
            self.handle_arp_packet(packet)
        if isinstance(packet, packets.ICMP):
            self.handle_icmp_packet(packet)
        
    def update_arp_table(self, arp_packet):
        self.arp_table[arp_packet.get_src_ip()] = [arp_packet.get_src_mac(), arp_packet.get_device_object(), 5]
    
    def refresh_arp_table(self):
        for entry in self.arp_table:
            if self.arp_table[entry][2] > 1:
                self.arp_table[entry][2] -= 1
            else:
                del self.arp_table[entry]

    def update_routing_table(self, router_source, routing_info):
        networks = routing_info.split(" ")
        aggregate = address_aggregation(networks)
        self.add_route(aggregate, router_source)
        "WRITE ADDRESS AGGREGATION HELPER"

    def update_neighbors(self):
        information = "DHCP_UPDATE: "
        for dir_conn_net in self.routing_table:
            information += dir_conn_net
        for network in self.routing_table:
            dhcp_update = self.generate_udp_packet(self.routing_table[network], information)
            self.forward_packet(dhcp_update)

""" +++++++++++++++++++----++++++++++++++++++++++ """
""" ++++++++++++++++++|HOST|+++++++++++++++++++++ """
""" +++++++++++++++++++----++++++++++++++++++++++ """

class Host:
    def __init__(self, name, mac_address, controller):
        self.controller = controller
        self.name = name
        self.mac_address = mac_address
        self.ip_address = None
        self.gateway_router = None
        self.routing_table = {"0.0.0.0/0" : None} # {network : next_hop_ip} ?
        self.arp_table = {}

    def get_name(self):
        return self.name

    def get_gateway_router(self):
        return self.gateway_router

    def set_gateway_router(self, router_obj):
        self.gateway_router = router_obj
    
    def get_ip_address(self):
        return self.ip_address

    def set_ip_address(self, ip_address):
        self.ip_address = ip_address

    def add_route(self, dest_network, next_hop):
        self.routing_table[dest_network] = next_hop


    def remove_route(self, dest_network, next_hop):
        if dest_network in self.routing_table:
            if self.routing_table[dest_network] == next_hop:
                del self.routing_table[dest_network]
    

    def clear_routing_table(self):
        self.routing_table = {}
            
    
    def get_next_hop(self, dest_ip):
        next_hop = ""
        for addr in self.routing_table:
            if ip_to_bin(addr) in ip_to_bin(dst_ip) and len(ip_to_bin(addr)) > len(ip_to_bin(next_hop)):
                next_hop = addr
        return self.routing_table[next_hop]


    def forward_packet(self, packet):
        next_hop = self.get_next_hop(packet.get_dest_ip())
        if next_hop in self.arp_table:
            frame = Frame(self.mac_address, self.arp_table[next_hop][0], packet)
            next_hop_device = self.arp_table[next_hop][1]
            next_hop_device.handle_incoming_frame(frame)
        else:
            return False

    
    def generate_udp_packet(self, dest_ip, data = None):
        udp_packet = packets.UDP(self.ip_address, dest_ip, data)
        return udp_packet

    
    def handle_udp_packet(self, udp_packet):
        data = udp_packet.get_data()
        if data is not None:
            if data[:12] == "DHCP_UPDATE: ":
                self.update_routing_table(udp_packet.get_src_ip(), data)
            else:
                self.controller.listen(self.name, data)


    def generate_arp_request(self, dest_ip):
        arp_packet = ARP(self.ip_address, dest_ip, self.mac_address)
        return arp_packet


    def handle_arp_packet(self, arp_packet):
        if arp_packet.request:
            response_packet = packets.ARP(self.ip_address, self.mac, arp_packet.get_src_ip(), dest_mac=arp_packet.src_mac, device_object=self)
            self.forward_packet(response_packet)
            self.update_arp_table(arp_packet)
        else:
            self.update_arp_table(arp_packet)

    def generate_icmp_request(self, dest_ip):
        source = self.get_source_ip(dest_ip)
        icmp_packet = packets.ICMP(source, dest_ip, time.time(), request=True)
        return icmp_packet


    def handle_icmp_packet(self, icmp_packet):
        if icmp_packet.request:
            if icmp_packet.get_dest_ip() in self.address_table:
                response_packet = packets.ICMP(icmp_packet.get_dest_ip(), icmp_packet.get_src_ip(), icmp_packet.get_time())
                self.forward_packet(response_packet)
            else:
                self.forward_packet(icmp_packet)
        else:
            return str(icmp_packet.get_src_ip()) + " is live. RTT: " + str(round(icmp_packet.get_time(), 2))
            


    def handle_incoming_frame(self, frame):
        packet = frame.decapsulate()
        if isinstance(packet, packets.UDP):
            self.handle_udp_packet(packet)
        if isinstance(packet, packets.ARP):
            self.handle_arp_packet(packet)
        if isinstance(packet, packets.ICMP):
            self.handle_icmp_packet(packet)
    

    def update_routing_table(self, router_source, routing_info):
        networks = routing_info.split(" ")
        aggregate = address_aggregation(networks)
        self.add_route(aggregate, router_source)


""" +++++++++++++++++++------++++++++++++++++++++ """
""" ++++++++++++++++++|SWITCH|+++++++++++++++++++ """
""" +++++++++++++++++++------++++++++++++++++++++ """

class Switch:
    def __init__(self, name, mac_address):
        self.name = name
        self.mac_address = mac_address
        self.arp_table = {} # {ip_address : [mac_address, device object, timer]}
        self.arp_table = {} # {mac_address : [ip_address, device object, timer]}

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def update_arp_table(self, frame):
        self.arp_table[frame.get_src_mac()] = [frame.decapsulate().get_src_ip(), frame.get_src_object(), 5]
    
    def refresh_arp_table(self):
        for entry in self.arp_table:
            if self.arp_table[entry][2] > 1:
                self.arp_table[entry][2] -= 1
            else:
                del self.arp_table[entry]
    
    def handle_incoming_frame(self, frame):
        if frame.get_dest_mac() in self.arp_table:
            self.arp_table[frame.get_dest_mac()][1].handle_incoming_frame(frame)

""" ++++++++++++++++----------------++++++++++++++++++ """
""" +++++++++++++++|HELPER FUNCTIONS|+++++++++++++++++ """
""" ++++++++++++++++----------------++++++++++++++++++ """

def ip_to_bin(ip_address):
    try:
        idx = ip_address.index('/')
        mask = int(ip_address[idx:])
        ip_address = ip_address[:idx]
    except ValueError:
        mask = 32
     
    binary_addr = ""
    for octet in ip_address.split('.'):
        binary_octet = format(int(octet), "08b")
        binary_addr += binary_octet

    mask += len(binary_addr)
    return binary_addr[:mask]

def address_aggregation(networks):
    network_objects = [ipaddress.ip_network(network) for network in networks]
    aggregated = ipaddress.collapse_addresses(network_objects)
    
    return [str(network) for network in aggregated]