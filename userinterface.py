import sys
from network import *
from devices import *
from helperfunctions import *

# MAIN MENU
def mainMenu(network):
    while True:
        print("\nOptions:")
        print("A: View Network") # Done
        print("B: View LANs") # Done
        print("C: Edit Network") # Done?
        print("D: Interact With The Network") # Working On
        print("E: Quit") # Done
        a = input("What would you like to do [A,B,C,D,E]: ").upper()
        print("\n")

        if a == "A":
            print(network)
            x = input("Press Return To View Options")

        elif a == "B":
            print(network.view_lans())
            x = input("Press Return To View Options")

        elif a == "C":
            edit_network(network)
            continue

        elif a == "D":
            interact(network)
            continue

        else:
            sys.exit()


# EDIT_NETWORK MENU (Separate LAN Menu attached)
def edit_network(network):
    while True:
        print("\nOptions:")
        print("A: View Network") # Done
        print("B: View LANs") # Done 
        print("C: Add LAN") # Done
        print("D: Remove LAN") # Done
        print("E: Edit A LAN") # Done, but unsure about edit_lan()
        print("F: Exit") # Done
        a = input("What would you like to do [A,B,C,D,E]: ").upper()
        print("\n")

        # View Network
        if a == "A":
            print(network)
            x = input("Press Return To Options")
            continue

        # View LANs
        elif a == "B": 
            print(network.view_lans())
            x = input("Press Return To Options")
            continue

        # Add LAN
        elif a == "C":
            # initiating new LAN(name, lan_address, router, network)
            # Input LAN Name
            lan_name = input("Enter New LAN Name: ")
            while lan_name in network.LANs or lan_name in network.LANs.devices:
                lan_name = input(name, "Invalid Name, Try A Different Name: ")
            # Input LAN Address
            lan_address = input("Enter A /24 Network Address: ") #A Bit unsafe, but were going to assume they enter 1.2.3.4 and not 1.2.3.4/24
            while not network.address_available(lan_address):
                lan_address = input(lan_address, "Address Not Available, Try A Different Address: ")

            # Use Existing Router
            if input("Create LAN From New Or Existing Router? [New, Existing]: ") == "New":
                router_name = input("Enter Router Name: ")
                while router_name in network.LANs or name in network.LANs.devices:
                    router_name = input(router_name, "Invalid Name, Try A Different Name: ")
                lan_router = Router(router_name, mac_gen())
            
            # Create New Router
            else:
                router_name = input("Enter The Name Of An Existing Router: ")
                while (router_name not in network.LANs.devices) or (network.LANs.devices[router_name] is not isinstance(Router)):
                    router_name = input(router_name, "Invalid Name, Try A Different Name: ")
                lan_router = network.LANs.devices[router_name]
                lan_router.add_interface[lan_address] = None #May have to edit this bc of the router interface table
            # Create LAN instance
            lan = LAN(lan_name, lan_address, lan_router, network)
            print("LAN Created Successfully Under ", lan_address)
            continue

        # Remove LAN
        elif a == "D":
            lan_name = input("Enter The Name Of The LAN You Wish To Remove: ")
            while lan_name not in network.LANs:
                lan_name = input(lan_name, "Invalid Name, Try A Different Name: ")
            which_lan = network.LANs[lan_name]
            
            if input("Are You Sure? You Will Also Be Removing All", which_lan.num_devices, "On The LAN. [Y/N] ") == "Y":
                which_lan.clear_lan()
                del network.LANs[lan_name]

            else:
                continue
        
        # Edit A LAN
        elif a == "E":
            lan_name = input("Enter The Name Of The LAN You Wish To Edit: ")
            while lan_name not in network.LANs:
                lan_name = input("Invalid Name, Try A Different Name: ")
            edit_LAN(network.LANs[lan_name], network)
            print(lan_name, "Modified Successfully")

        else:
            break


# EDIT_LAN MENU (via edit_network())
def edit_LAN(lan, network):
    while True:
        print("\nOptions:")
        print("A: View LAN") #Done
        print("B: Add Host") # Done
        print("C: Remove Host") #Done
        print("D: Reset LAN") #Done
        print("E: Exit") #Done
        a = input("What would you like to do [A,B,C,D,E]: ").upper()
        print("\n")

        # View LAN
        if a == "A":
            print(lan)
            x = input("Press Return To View Options")
            continue

        # Add Host
        elif a == "B":
            # Check if LAN is full
            if not (lan.num_hosts < 16 and (int(lan.network_address[-3:]) + lan.num_hosts < 255)):
                print("Error: LAN Full")
                continue

            # Start Configuring Host... 
            # Input Host Name:
            host_name = input("Enter New Host Name: ")
            while host_name in lan.devices:
                host_name = input("Invalid Name, Try A Diffreent Name: ")
            # Host ip_address:
            host_ip = lan.network_address[:-3] + str(int(lan.network_address[-3:]) + lan.num_hosts + 1)
            # Host MAC:
            host_mac = mac_gen()
            # Initiate Host
            new_host = Host(name, host_mac, host_ip)

            # If LAN has switch, add device to switch otherwise connect directly to gateway
            if lan.switch:
                lan.switch.add_interface(new_host)
            else:
                lan.gateway_router.add_interface(lan.network_address, new_host)

            # Add host to LAN. LAN will add it to network automatically
            lan.add_host(new_host)
            continue

        # Remove Host
        elif a == "C":
            # Get Host Name
            host_name = input("Enter The Name Of The Host You Want To Remove: ")
            while host_name not in lan.devices:
                host_name = input("Invalid Name, Try A Diffreent Name: ")
            
            # Get Host Object
            host = lan.devices[host_name]

            # Remove host from the switch interface if the LAN has a switch
            if lan.switch != None:
                lan.switch.remove_interface(host)
            lan.remove_host(host)
            continue

        # Reset LAN
        elif a == "D":
            if input("Are You Sure? You Will Also Be Removing All", lan.num_devices, "On The LAN. [Y/N] ") == "Y":
                lan.clear_lan()
                break
            continue

        else:
            break


# NETWORK INTERACTION MENU
def interact(network):
    while True:
        print("\nOptions:")
        print("A: View Network") # Done
        print("B: View LANs") # Done
        print("C: Send Packet") # Working On
        print("D: Exit") # Done
        a = input("What would you like to do [A,B,C,D]: ").upper()
        print("\n")

        # View Network
        if a == "A":
            print(network)
            x = input("Press Return To View Options")
            continue

        # View LANs
        elif a == "B":
            print(network.view_lans())
            x = input("Press Return To View Options")
            continue

        # Send Packet
        elif a == "C":
            src_ip = input("Enter The Source Device IP address: ")
            while src_ip not in network.hosts:
                src_ip = input("Source IP Does Not Belong To A Host. Enter A Source Host IP Address: ")
            dst_ip = input("Enter Destination Device IP address: ")
            while dst_ip not in network.hosts or dst_ip == src_ip:
                print("Destination IP Does Not Belong To A Host Or Is Same As Source.")
                dst_ip = input("Enter A Destination Host IP Address: ")
            
            packet_data = input("Enter Packet Data: ")
            frame = Packet(src_ip, dst_ip, packet_data)
            network.hosts[src_ip].receive_frame()

            continue

        else:
            break


### MAIN LOOP
def main():
    MainNetwork = Network()
    L1 = LAN("L1", "192.168.0.0", Router("R1", mac_gen()), MainNetwork)
    print("************************")
    print("Peter's Network Emulator")
    print("************************\n")

    print("Each Emulation Starts With A LAN 'L1' (192.168.0.0/24) And Its Gateway Router 'R1' (192.168.0.1)\n\n")

    mainMenu(MainNetwork)
    
if __name__ == "__main__":
    main()