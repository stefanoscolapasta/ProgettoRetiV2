import socket as sk
import time, pickle, os, random
from datetime import datetime
from IOT_device_UDP import Measurement

class Gateway:

    DHCP_PORT = 1075
    devices = {} # {ip_address: measurements}

    def __init__(self):
        self.udp_sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.udp_sock.bind(('localhost', 6001))
        self.dhcp_address = ('localhost', self.DHCP_PORT)
        self.udp_receive_mac = "AF:E8:23:B4:00:D2"
        self.udp_receive_ip_address = "192.168.1.1"
        self.open_tcp_socket()   

    def get_udp_interface_ip_address(self):
        return self.udp_receive_ip_address

    def open_tcp_socket(self):
        self.tcp_sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.tcp_server_address = ('localhost', 3001)

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
        self.open_tcp_socket()
        self.clear_measurments()
    
    def clear_measurments(self):
        self.get_devices().clear()
    
    def confirm_reception(self, address):
        self.get_udp_sock().sendto("Measurment has been delivered".encode("utf-8"), address)

    def discard_reception(self, address):
        self.get_udp_sock().sendto("Wrong Ip address".encode("utf-8"), address)

def main():
    gateway = Gateway()
    # Attendo che i devices si colleghino
    while True:
        print("Gateway waiting to receive data from device")
        data, real_address = gateway.get_udp_sock().recvfrom(4096)
        print("Data received from device ", real_address)
        arrival_time = time.perf_counter_ns()
        ip_address, gateway_ip, time_of_sending , measurements = pickle.loads(data)
        #Effettuiamo controllo se indirizzo ip del gateway ip coincide con quello attuale corretto
        if gateway_ip == gateway.get_udp_interface_ip_address():
            print("Time to receive UDP datagram: ", (arrival_time - time_of_sending))
            print("Data received from device with ip address: ", ip_address)
            # controllo che non si tratti di misurazioni gia inviate
            if ip_address not in gateway.get_devices().keys():
                gateway.get_devices()[ip_address] = measurements
            # invio conferma di ricezione al device
            gateway.confirm_reception(real_address)
            # non appena ho ricevuto le misurazioni dai 4 device invio
            # i dati al server    
            if (len(gateway.get_devices().keys())) == 1:
                gateway.send_data_to_server()
        else:
            gateway.discard_reception(real_address)

if __name__ == '__main__':
    main()