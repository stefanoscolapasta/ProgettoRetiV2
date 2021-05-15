import socket as sk
import time, pickle, os, random
from datetime import datetime
from IOT_device_UDP import Measurement

class Gateway:

    DHCP_PORT = 1075
    devices = {} # {address: measurements}
    devices_connection_address = {} # {ip_address: connection_address}

    def __init__(self, mac_address):
        self.mac_address = mac_address
        self.udp_sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.udp_sock.bind(('localhost', 6001))
        self.dhcp_address = ('localhost', self.DHCP_PORT)
        self.udp_receive_address = self.retrieve_address_from_dhcp_server()
        self.reopen_tcp_socket()   

    def retrieve_address_from_dhcp_server(self):
        self.udp_sock.sendto(str(self.mac_address).encode('utf-8'), self.dhcp_address)
        data, server = self.udp_sock.recvfrom(4096)
        if data:
            return data.decode('utf-8')
        return ''

    def reopen_tcp_socket(self):
        self.tcp_sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.tcp_server_address = ('localhost', 3001)

    def get_connections_address(self):
        return self.devices_connection_address

    def get_udp_sock(self):
        return self.udp_sock

    def get_tcp_sock(self):
        return self.tcp_sock
    
    def get_devices(self):
        return self.devices
    
    def get_device(self, address):
        if address in self.devices.keys():
            return self.devices[address]
        return "Not present"

    def send_data_to_server(self):
        try:
            self.get_tcp_sock().connect(self.tcp_server_address)
            self.get_tcp_sock().send(pickle.dumps(self.get_devices()))
        except Exception as error:
            print(error)
        message = self.get_tcp_sock().recv(1024)
        print(message.decode("utf-8"))
        self.get_tcp_sock().close()
        self.reopen_tcp_socket()
    
    def confirm_reception(self):
        for address in self.get_devices().keys():
            self.get_udp_sock().sendto("Measurment has been delivered".encode("utf-8"), self.get_connections_address()[address])

def main():
    gateway_mac_address = str(input("Inserisci indirizzo mac del gateway: "))
    gateway = Gateway(gateway_mac_address)
    # Attendo che i devices si colleghino
    while True:
        data, real_address = gateway.get_udp_sock().recvfrom(4096)
        ip_address, measurements = pickle.loads(data)
        gateway.get_connections_address()[ip_address] = real_address
        gateway.get_devices()[ip_address] = measurements
        if (len(gateway.get_devices().keys())) == 1:
            gateway.send_data_to_server()
        gateway.confirm_reception()
            
if __name__ == '__main__':
    main()