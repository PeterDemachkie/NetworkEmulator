# Peter Demachkie
# bridge.py
# www.github.com/PeterDemachkie/NetworkEmulator
# peterdemachkie101@gmail.com

from networkdevices import *
import ipaddress
import random
import json

class Network:
    def __init__(self):
        self.routers = {} #object : name
        self.hosts = {} # object : (name, ip_address)
        self.switches = {} # object : name
        self.networks = {} # network_address: [gateway_router, switch_obj, [device_objects]]
        self.messages = [] # (host_name, message)

    "ACCESS FUNCTIONS"

    def is_router(self, name):
        return name in self.routers.values()

    def is_host(self, name):
        return name in [value[0] for value in self.hosts.values()]

    def is_switch(self, name):
        return name in self.switches.values()

    def is_device(self, name):
        return self.is_host(name) or self.is_host(name) or self.is_switch(name)

    def is_network(self, network_address):
        return network_address in self.networks.keys()

    def get_host_ip(self, name):
        if name in [value[0] for value in self.hosts.values()]:
            return self.hosts[name][1]
        return False

    def get_networks(self):
        return self.networks.keys()

    def get_available_addresses(self, network_address):
        network = ipaddress.IPv4Network(network_address, strict=False)
        all_addresses = [str(ip) for ip in network.hosts()]
        taken_addresses = []
        for obj in self.networks[network_address][2]:
            if self.is_host(obj.get_name()):
                taken_addresses.append(obj.get_ip_address())
            if self.is_router(obj.get_name()):
                taken_addresses.append(obj.get_ip_address(network_address))
        occupied_addresses = [address for address in all_addresses if address not in taken_addresses]
        return occupied_addresses

    def add_network(self, network_address, router_object):
        self.networks[network_address] = [router_object, None, 0]

    def remove_network(self, network_address):
        del self.networks[network_address]

    def view_network(self):
        ret_str = "Network Topology:\n"
        for network_address in self.networks.keys():
            ret_str += self.view_subnet(network_address)
        return ret_str
        
    def view_subnet(self, network_address):
        network = self.networks[network_address]
        ret_str = "Subnet " + network_address + ":\n"
        if network[1] is not None:
            switch_name = network[1].get_name()
            ret_str += "Gateway Router " + network[0].get_name() + " <-> Switch " + switch_name
            for device in network[2]:
                if self.is_host(device.get_name()):
                    ret_str += "\nSwitch " + switch_name + " <-> " + device.get_name() + " (" + device.get_ip_address() + ")"
                if self.is_router(device.get_name()) and device is not network[0]:
                    ret_str += "\nSwitch " + switch_name + " <-> " + device.get_name() + " (" + device.get_ip_address(network_address) + ")"
        return ret_str
            # Again this is something I need network-device information for
            # At least to do it cleanly and easily

    def send_packet(self, source, dest, packet_type, data=None):
        host_object = None
        for host, attributes in self.hosts.items():
            if attributes[0] == source:
                host_object = host
        if packet_type == "UDP":
            packet = host_object.generate_udp_packet(dest, data)
        if packet_type == "ICMP":
            packet = host_object.generate_icmp_request(dest)
        host_object.forward_packet(packet)

    def read(self):
        message = self.messages.pop()
        return message[0] + ": " + message[1]

    def listen(self, host, data):
        self.messages.append((device, data))

    def new_router(self, name, network_address):
        mac_address = mac_gen()
        router = Router(name, mac_address, self)
        if self.is_network(network_address): #if router is being added to existing network...
            if self.networks[network_address][1] is not None:
                next_hop_object = self.networks[network_address][1]
                router.add_route(network_address, next_hop_object)
            else:
                next_hop_object = self.networks[network_address][0]
            router.update_neighbors()
            self.networks[network_address][2].append(router)
        else:
            self.networks[network_address] = [router, None, [router]]
        self.routers[router] = name
        ip_address = self.get_available_addresses(network_address).pop()
        router.add_network(ip_address, network_address)

        #THINGS TO DO WHEN ADDING A ROUTER TO THE NETWORK:
        #Add it to the router table
        #update network table

    def add_router_network(self, router_name, network_address):
        for router_object, name in self.routers.items():
            if name == router_name:
                router = router_object 
        if network_address in router.get_networks():
            if self.networks[network_address][1] is not None:
                router.add_route(network_address, self.networks[network_address][1])
            else:
                router.add_route(network_address, self.networks[network_address][0])
        router.update_neighbors()
            
            #WORK ON

    def remove_router_network(self, router_name, network_address):
        # Check if there is another router on the subnet and make it the new gateway
            # (it might already be the gateway but its fine)
            # Need to set every hosts defaul gateway to the new router
            # I should do that with packets but whatever idc
        # If there isnt another router, nuke the whole network EXCEPT this router
        new_gateway = None
        for device in self.networks[network_address]:
            if self.is_router(device) and device.get_name() != router_name:
                new_gateway = device
                break
        if new_gateway is not None:
            for device in self.networks[network_address]:
                if self.is_host(device):
                    device.set_gateway_router(new_gateway)
        else:
            if self.networks[network_address][1] is not None:
                self.remove_switch(self.networks[network_address][1].get_name())
            else:
                for device in self.networks[network_address]:
                    if self.is_host(device):
                        self.remove_host(device.get_name())
        del self.networks[network_address]

        #WORK ON:
        # NEED TO UPDATE 

    def remove_router(self, router):
        # Call remove_router_network on each of the router's networks
        # Then Remove the router itself
        # Update Neighbors...
        for network in router.get_networks():
            self.remove_router_network(network)
        
    def new_host(self, name, network_address):
        host = Host(name, mac_gen(), self)
        host.set_ip_address(self.get_available_addresses(network_address).pop(0))
        gateway = self.networks[network_address][0]
        host.set_gateway_router(gateway)
        if self.networks[network_address][1] is not None:
            host.add_route(network_address, self.networks[network_address][1])
        else:
            host.add_route(network_address, gateway)
        self.networks[network_address][2].append(host)
        self.hosts[host] = (name, host.get_ip_address)
        # WORK ON

    def remove_host(self, name):
        #Host must be removed from gateway router routes
        #Removed from switch table if applicable
        #network device count removed
        #network address freed up
        #host removed from self.hosts
        host_network = None
        for network, attributes in self.networks.items():
            if name in attributes[2]:
                host_network = network

        router = self.networks[network][0]
        for host in self.hosts:
            if self.hosts[host] == name:
                del self.hosts[host]
                router.remove_route(host.get_ip_address())
        #WORK ON

    def new_switch(self, name, network_address):
        mac_address = mac_gen()
        router = self.networks[network_address][0]
        switch = Switch(name, mac_address)
        router.add_route(network_address, switch)
        if len(self.networks[network_address][2]) > 1:
            # Its safe here to assume that no switch is on the sub network
            for device in self.networks[network_address][2]:
                if self.is_host(device):
                    device.add_route(network_address, switch)
        self.networks[network_address][1] = switch

    def remove_switch(self, name):
        switch = None
        for switch_obj, switch_name in self.switches.items():
            if switch_name == name:
                switch = switch_obj
        network_address = None
        for network, attributes in self.networks.items():
            if attributes[1] == switch:
                network_address = network
        for device in self.networks[network_address][2]:
            if self.is_host(device):
                self.remove_host(device)
        # Remove Switch Itelf...
        # Need To Make Decisions regarding non-gateway routers on network
        #WORK ON
        "NOT FINISHED!!!"

    def save(self, filename):
        outfile = filename + ".json"
        return
        #WORK ON

    def load(self, filename):
        json_file = open(filename)
        data = json.load(json_file)
        #WORK ON


def is_ipv4(address):
    try:
        ipaddress.IPv4Address(address)
        return True
    except ipaddress.AddressValueError:
        return False

def mac_gen():
    mac = [random.randint(0x00, 0xff) for _ in range(6)]
    mac_address = ":".join([format(byte, "02X") for byte in mac])
    return mac_address
