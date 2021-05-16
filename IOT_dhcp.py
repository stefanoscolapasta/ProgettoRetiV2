import socket as sk
import time

# Creiamo il socket
sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

server_address = ('localhost', 1075)
print ('\n\r starting up on %s port %s' % server_address)
sock.bind(server_address)
arp_table = {} # {MAC-address: ip-address}

def find_available_ip(arp_table):
    network_number = "192.168.1."
    host_number = 2
    if len(arp_table.values()) != 0: 
        host_number = int(max(arp_table.values(), key = lambda x: int(x.split(".")[3])).split(".")[3]) + 1
    if len(arp_table.values()) == 254:
        return "0.0.0.0"
    return str(network_number) + str(host_number) 

while True:
    print('\n\r waiting to receive message...')
    # ascolto richieste di indirizzi ip
    data, address = sock.recvfrom(1024)
    print("Received request for:",data)
    mac_address = data.decode('utf-8')
    if mac_address not in arp_table.keys():
        print("New device is requiring IP address")
        new_available_ip_address = find_available_ip(arp_table)
        print("Device ", mac_address, " is granted of ", new_available_ip_address, " ip address")
        arp_table[mac_address] = new_available_ip_address
        
    sock.sendto(arp_table[mac_address].encode('utf-8'), address)
