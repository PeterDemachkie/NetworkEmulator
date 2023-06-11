#Helper Functions
import random
from devices, network import *
#First, checks if there is a mask at the end of the ip (/24 for example)
#If there is, it saves the number and removes it from the string
#If not the mask is just set to 32

#Then the ipv4 notation ip address is changed to binary
#Then the binary address is sliced to the length of the network mask,
#If there wasnt one, it wont be shortened at all
def ip_to_bin(ip_address):
    try:
        idx = ip_address.index('/')
        mask = int(ip_address[idx:])
        ip_address = ip_address[:idx]
    except ValueError:
        mask = 32
     
    for octet in ip_address.split('.'):
        binary_octet = format(int(octet), "08b")
        binary_addr += binary_octet

    mask += len(binary_addr)//8
    return binary_addr[:mask]

def bin_to_ip(ip_address):
    

#Currently works if a network address just ends at its mask... but not if it doesnt and idk how to deal with masks yet

#I need to compare 192.30.0.0/24 to 192.30.15.15
#We need to figure out how to just compare the first (mask) digits of binary to the entirety of the second ip
#So we need to cut the ip address at that point
def subnet_route(dst_ip, routing_table):
    largest_subst = ""
    for addr in routing_table.keys():
        if ip_to_bin(addr) in ip_to_bin(dst_ip) and len(ip_to_bin(addr)) > len(ip_to_bin(largest_subst)):
            largest_subst = addr
    return largest_subst


#Generates random mac address, no collision detection though bc I dont care theres not gonna be any ffs
def mac_gen():
    mac = [random.randint(0x00, 0xff) for _ in range(6)]
    mac_address = ":".join([format(byte, "02X") for byte in mac])
    return mac_address

def ip_gen():

def is_ipv4(address):
    parts = address.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            value = int(part)
            if value < 0 or value > 255:
                return False
        except ValueError:
            return False
    
    return True

def 