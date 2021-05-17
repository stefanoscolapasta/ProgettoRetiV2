import socket as sk
import time, pickle

class SimpleDhcp:

    def __init__(self):
        self.server_address = ('localhost', 1075)
        self.udp_sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.udp_sock.bind(self.server_address)
        self.arp_table = {}
        self.network_number = "192.168.1."
        self.gateway_address = "192.168.1.1"
        self.gateway_mac_address = "AF:E8:23:B4:00:D2"
        self.arp_table[self.gateway_mac_address] = self.gateway_address

    def get_udp_sock(self):
        return self.udp_sock

    def find_available_ip_address(self):
        host_number = 2
        if len(self.arp_table.values()) != 0: 
            host_number = int(max(self.arp_table.values(), key = lambda x: int(x.split(".")[3])).split(".")[3]) + 1
        if len(self.arp_table.values()) == 254:
            return "0.0.0.0"
        return str(self.network_number) + str(host_number)     

    def get_arp_table(self):
        return self.arp_table

    def get_gateway_address(self):
        return self.gateway_address

def main():

    dhcp_udp_server = SimpleDhcp()

    while True:
        print('\n\r waiting to receive message...')
        # ascolto richieste di indirizzi ip
        data, address = dhcp_udp_server.get_udp_sock().recvfrom(1024)
        print("Received request for:",data)
        mac_address = data.decode('utf-8')
        if mac_address not in dhcp_udp_server.get_arp_table().keys():

            print("New device is requiring IP address")
            new_available_ip_address = dhcp_udp_server.find_available_ip_address()
            print("Device ", mac_address, " is granted of ", new_available_ip_address, " ip address")
            dhcp_udp_server.get_arp_table()[mac_address] = new_available_ip_address
            
        
        dhcp_udp_server.get_udp_sock().sendto(str(str(dhcp_udp_server.get_arp_table().get(mac_address)) + "_" + str(dhcp_udp_server.get_gateway_address())).encode('utf-8') , address)


if __name__ == '__main__':
    main()