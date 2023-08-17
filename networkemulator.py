# Peter Demachkie
# userinterface.py
# www.github.com/PeterDemachkie/NetworkEmulator
# peterdemachkie101@gmail.com

import sys
import os
import controller

def start_page():
    print("\nWelcome To Network Emulator")
    print("To View Documentation Visit github.com/PeterDemachkie/NetworkEmulator")
    network = controller.Network()
    main_menu(network)


def main_menu(network):
    # initiate network
    while True:
        print("\nChoose from the options below [1-7]: ")
        print("[1]: View Network Details") #Done
        print("[2]: View Subnet Details") #Done
        print("[3]: Interact With Network")
        print("[4]: Edit Network Topology")
        print("[5]: Save Topology")
        print("[6]: Load Topology")
        print("[7]: Quit")
        mm_response = input("")
        print("")

        if mm_response == "1":
            view_network(network)
        elif mm_response == "2":
            view_subnet(network)
        elif mm_response == "3":
            interact_network(network)
        elif mm_response == "4":
            edit_menu(network)
        elif mm_response == "5":
            save_network(network)
        elif mm_response == "6":
            load_network(network)
        elif mm_response == "7":
                sys.exit(0)
        else:
            continue

def view_network(network):
    print(network.view_network())

def view_subnet(network):
    which_subnet = input("Which Subnet Would You Like To View? (Enter Subnet Address): ")
    while not network.is_network(which_subnet):
        print("Invalid Subnet Address")
        which_subnet = input("Which Subnet Would You Like To View? (Enter Subnet Address): ")
    print(network.view_subnet(which_subnet))

def interact_network(network):
    packet_type = input("What Kind Of Packet Do You Want To Send? (UDP or ICMP): ").upper()
    while packet_type not in ["UDP", "ICMP"]:
        print("Incorrect Packet Type [UDP, ICMP]")
        packet_type = input("What Kind Of Packet Do You Want To Send?: ")
    
    print("Enter The Names Of The Source And Destination Hosts")
    print("Example: PC1 PC3")
    responses = input("").split(" ")
    while True:
        if len(responses) != 2:
            print("Incorrect Number Of Inputs")
            responses = input("").split(" ")
            continue
        source, dest = responses
        if not network.is_host(source) or not network.is_host(dest):
            print("Either Source Or Destination Is Not A Host")
            responses = input("").split(" ")
            continue
        break

    data = None
    if packet_type == "UDP":
        data = input("Enter The Data For The UDP Packet: ")
    network.send_packet(source, dest, packet_type, data)
    print(network.read())

def edit_menu(network):
    print("Choose From The Options Below[1-4]:")
    print("[1]: Edit Routers (Add, Edit, Or Remove)")
    print("[2]: Edit Hosts (Add Or Remove)")
    print("[3]: Edit Switches (Add Or Remove)")
    print("[4]: Go Back To Main Menu")
    em_response = input("")
    print("")

    if em_response == "1":
        option = input("Would You Like To [ADD], [EDIT], Or [REMOVE] A Router?: ").upper()
        if option == "ADD":
            router_name = input("Enter The Name Of The New Router: ")
            while network.is_device(router_name):
                print("Device Name Already Taken")
                router_name = input("Enter The Name Of The New Router: ")
            network_address = input("Enter Either The Network Address Of An Existing Network, Or An Unused Network Address: ")
            if network.is_network(network_address):
                print("Creating New Network " + network_address, " On Router " + router_name)
            network.new_router(router_name, network_address)

        elif option == "EDIT":
            which_router = input("Enter The Name Of Router Would You Like To Edit: ")
            while not network.is_router(which_router):
                print("Invalid Router Name")
                which_router = input("Enter The Name Of Router Would You Like To Edit: ")
            how_edit = input("Would You Like To [ADD] Or [REMOVE] A Connection: ").upper()
            if how_edit == "ADD":
                network_address = input("Enter A New Or Existing Network Address: ")
                while len(network.get_available_addresses(network_address)) < 0:
                    print("Network Full")
                    network_address = input("Enter A New Or Existing Network Address: ")
                network.add_router_network(which_router, network_address)
            else:
                network_address = input("Enter The Network Address You Would Like To Remove: ")
                while not network.is_network(network_address):
                    print("Invalid Network Address")
                    network_address = input("Enter The Network Address You Would Like To Remove: ")
                confirm = input("Warning: Removing This Route Will Remove Any Connected Devices. \nContinue? [Y/N]: ")
                if confirm == "Y":
                    network.remove_router_network(router, network_address)

        else:
            which_router = input("Enter The Name Of Router Would You Like To Remove: ")
            while not network.is_router(which_router):
                print("Invalid Router Name")
                which_router = input("Enter The Name Of Router Would You Like To Edit: ")
            confirm = input("Warning: Removing This Router Will Remove Any Connected Devices. \nContinue? [Y/N]: ")
            if confirm == "Y":
                network.remove_router(router)
            

    elif em_response == "2":
        option = input("Would You Like To [ADD] Or [REMOVE] A Host?: ").upper()
        if option == "ADD":
            host_name = input("Enter The Name Of The New Host: ")
            while network.is_device(host_name):
                print("Device Name Already Taken")
                host_name = input("Enter The Name Of The New Host: ")
            network_address = input("Enter The Name Of The Network You Would Like " + host_name + " To Be Part Of: ")
            while not network.is_network(network_address):
                print("Invalid Network Address")
                network_address = input("Enter The Address Of The Network You Would Like " + host_name + " To Be Part Of: ")
            network.new_host(host_name, network_address)
        else:
            host_name = input("Enter The Name Of The Host You Want To Remove: ")
            while not network.is_host(host_name):
                print("Invalid Host Name")
                host_name = input("Enter The Name Of The Host You Want To Remove: ")
            confirm = input("Warning: Removing" + host_name + "\nContinue? [Y/N]: ")
            if confirm == "Y":
                network.remove_host(host_name)
        return

    elif em_response == "3":
        option = input("Would You Like To [ADD] Or [REMOVE] A Switch?: ").upper()
        if option == "ADD":
            switch_name = input("Enter The Name Of The New Switch: ")
            while network.is_device(switch_name):
                print("Device Name Already Taken")
            network_address = input("Enter The Address Of The Network You Would Like " + switch_name + " To Be Part Of: ")
            while True:
                if not network.is_network(network_address):
                    print("Invalid Network Address")
                    network_address = input("Enter The Address Of The Network You Would Like " + switch_name + " To Be Part Of: ")
                    continue
                elif len(network.networks[network_address][2]) > 1:
                    print("Subnet Already Set With A Host Or Switch")
                    network_address = input("Enter The Address Of The Network You Would Like " + switch_name + " To Be Part Of: ")
                    
                    continue
                else:
                    break
            network.new_switch(switch_name, network_address)
            print("Successfully Added " + switch_name + " On Network " + network_address)
        else:
            which_switch = input("Enter The Name Of The Switch You Want To Remove: ")
            while not network.is_switch(which_switch):
                print("Invalid Switch")
                which_switch = input("Enter The Name Of The Switch You Want To Remove: ")
            confirm = input("Warning: Removing This Switch Will Remove Any Connected Hosts. \nContinue [Y/N]: ")
            if confirm == "Y":
                network.remove_switch(which_switch)
            return
    else:
        return

def save_network(network):
    while True:
        save_file = input("Enter The Name You Would Like The File To Be Saved Under: ")
        if os.path.exists(save_file):
            confirm = input(save_file, "Already Exists. Overwrite? [Y/N]: ").upper()
            if confirm == "Y":
                network.save(save_file)
                break
            else:
                continue
        else:
            network.save(save_file)
            break

def load_network():
    while True:
        load_file = input("Enter The Filepath Of Your .JSON Network File: ")
        try:
            json_file = open(load_file)
            break
        except FileNotFoundError:
            print("File", load_file, "Not Found")


""" ++++++++++++++++----------------++++++++++++++++++ """
""" +++++++++++++++|HELPER FUNCTIONS|+++++++++++++++++ """
""" ++++++++++++++++----------------++++++++++++++++++ """


if __name__ == "__main__":
    start_page()