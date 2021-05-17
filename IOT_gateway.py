import socket as sk
import time, pickle, os, random
from datetime import datetime
from IOT_device_UDP import Measurement
import network_config as nc
from IOT_simulation import Simulation
from IOT_packet import Packet

class Gateway:
    DHCP_PORT = 1075
    devices = {} # {ip_address: measurements}

    def __init__(self):
        self.sim = Simulation()
        self.udp_sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM) # socket per invio delle misurazioni
        # TODO socket per dhcp
        self.udp_sock.bind(nc.gateway_address)   

    def get_rcv_ip_address(self):
        return self.sim.get_gateway_recv_ip()

    def get_udp_sock(self):
        return self.udp_sock
    
    def get_devices(self):
        return self.devices

    def send_data_to_server(self):
        try:
            server_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
            server_socket.connect(nc.server_address)
            server_socket.send(
                pickle.dumps(Packet(self.sim.get_gateway_send_mac(),
                    self.sim.get_server_mac(),
                    self.sim.get_gateway_send_ip(),
                    self.sim.get_server_ip(),
                    self.get_devices()
                ))
            )
        except Exception as error:
            print(error)
        message = server_socket.recv(1024)
        server_socket.close()

        pkt = pickle.loads(message)
        print("Server answer:")
        print(pkt.to_string())
        self.clear_measurments()
    
    def clear_measurments(self):
        self.get_devices().clear()
    
    
    def send_answer(self, address, pkt, message):
        self.get_udp_sock().sendto(
            pickle.dumps(Packet(self.sim.get_gateway_recv_mac(),
                pkt.get_source_mac(),
                self.sim.get_gateway_recv_ip(),
                pkt.get_source_ip,
                message
            )
        ), address)

    def confirm_reception(self, address, pkt):
        self.send_answer(address, pkt, "Measurements received")

    def discard_reception(self, address, pkt):
        self.send_answer(address, pkt, "Wrong Ip address")

def main():
    gateway = Gateway()
    # Attendo che i devices si colleghino
    while True:
        print("Gateway waiting to receive data from device")
        data, real_address = gateway.get_udp_sock().recvfrom(4096)
        print("Data received from device ", real_address)
        arrival_time = time.time_ns()
        
        pkt = pickle.loads(data)
        print(pkt.to_string())
        time_for_receipt = arrival_time - pkt.get_sending_time()
        #Effettuiamo controllo se indirizzo ip del gateway ip coincide con quello attuale corretto
        if pkt.get_destination_ip() == gateway.get_rcv_ip_address():
            print("Time to receive UDP datagram: ", time_for_receipt, "ns")
            print("Data received from device with ip address: ", pkt.get_source_ip())
            # controllo che non si tratti di misurazioni gia inviate
            if pkt.get_source_ip() not in gateway.get_devices().keys():
                gateway.get_devices()[pkt.get_source_ip()] = pkt.get_payload()
            else:
                print("Discarding, waiting for other devices...")
            # invio conferma di ricezione al device
            gateway.confirm_reception(real_address, pkt)
            # non appena ho ricevuto le misurazioni dagli n device invio
            # i dati al server    
            n=2
            if (len(gateway.get_devices().keys())) == n:
                gateway.send_data_to_server()
        else:
            gateway.discard_reception(real_address, pkt)

if __name__ == '__main__':
    main()