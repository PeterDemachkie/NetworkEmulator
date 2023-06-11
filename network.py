from helperfunctions import *
from devices import *

class LAN:
    def __init__(self, lan_name, network_address, router, network):
        self.name = lan_name
        self.network_address = "" #192.168.1.0 Each lan is going to automatically be on a /24
        self.num_hosts = 0 # Each LAN is going to be capped at 16 Hosts. (255.255.255.0-15)
        self.gateway_router = router
        self.devices = {} # {device name : device object}
        self.switch = None
        self.network = network
        network.add_LAN(self)

    def addHost(self, host): # Formerly add_host
        if self.num_hosts < 8:
            self.devices[device.name] = host
            self.network.add_host(host)
        else:
            print("Device capactity on ", self.name, "reached")

    def removeHost(self, host): #Formerly remove_host
        self.num_hosts -= 1
        del self.devices[host.name]
        self.network.remove_host(host)

    def addRouter(self, router):
        if self.num_hosts < 16:
            self.devices[device.name] = router
            self.network.add_host(router)
            self.num_hosts += 1
            
        else:
            print(self.name, "device capactity reached")

    def removeRouter(self, router):
        if router.isGateway(self):
            for name, device in self.devices:
                if isinstance(device, Router):
                    if device.isGateway(self):
                        self.setGateway(device)
                if router is self.gateway_router:
                    return False
        # If the router isnt the gateway router
        else:
            router.remove_interface(self)

    def setGateway(self, router):
        # change every devices gateway address to new router
        if router is not self.gateway_router:
            self.gateway_router = router
            

    def address_in_network(self, address):
        pass

    # Clear LAN Leaves lan in its base state. One Gateway router with a network interface
    def clear_lan(self):
        for name, device in self.devices:
            if isinstance(device, Router):
                if device != self.gateway_router:
                    device.remove_interface()
            else:
                del self.devices[name]

        self.num_hosts = 0

    def __str__(self):
        s = "LAN: " + self.name + ":\n"
        for name in self.devices:
            s += "\t" + name
        return s

#LAN rules:
# A LAN has to have at least one router (gateway) which will have the first available address in the subnet
# When a lan is created, its router needs to connect to some kind of device on init
class Network:
    def __init__(self):
        self.devices = {} # {device MAC addr : device object}
        self.hosts = {} # {host IP addr : host object}
        self.LANs = {} # {lan name : lan object}

    def add_device(self, device):
        self.devices[device.mac_address] = device

    def remove_device(self, device):
        del self.devices[device.mac_address]

    def add_host(self, host):
        self.hosts[host.ip_address] = host

    def remove_host(self, host):
        del self.hosts[host.ip_address]

    def add_LAN(self, lan):
        self.LANs[lan.name] = lan

    def remove_LAN(self, lan):
        if lan in self.LANs:
            lan.clear_lan()
            del self.LANs[lan.name]

    def address_available(self, net_addr):
        if network_addr not in [lan.address for lan in network.LANs.values()]:
            return True
        return False

    def view_lans(self):
        s = ""
        for lan_name in LANs:
            s += lan_name + "\n"
        return s

    def __str__(self):
        s = ""
        for lan in self.LANs.values():
            s += str(lan) + "\n"
        return s