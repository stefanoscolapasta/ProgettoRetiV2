import socket as sk
import time, pickle
import network_config as nc
from IOT_simulation import Simulation
from IOT_packet import Packet
from threading import Thread
import utils

class SimpleDhcp(Thread):

    def __init__(self, socket):
        Thread.__init__(self)
        self.sim = Simulation()
        self.dhcp_sock = socket
        self.arp_table = {}
        self.network_number = "192.168.1."
        self.arp_table[self.sim.get_gateway_recv_mac()] = self.sim.get_gateway_recv_ip()

    def get_dhcp_sock(self):
        return self.dhcp_sock

    def find_available_ip_address(self):
        host_number = 2
        if len(self.arp_table.values()) != 0: 
            host_number = int(max(self.arp_table.values(), key = lambda x: int(x.split(".")[3])).split(".")[3]) + 1
        if len(self.arp_table.values()) == 254:
            return "0.0.0.0"
        return str(self.network_number) + str(host_number)     

    def get_arp_table(self):
        return self.arp_table

    def run(self):
        while True:
            print('\n\rWaiting to receive message...')
            # ascolto richieste di indirizzi ip
            data, address = self.dhcp_sock.recvfrom(1024)
            utils.print_pkt_size(data)
            pkt = pickle.loads(data)
            utils.print_packet_header(pkt, "IOT DEVICE")
            mac_address = pkt.get_source_mac()
            print("Received request for:",mac_address)
            if mac_address not in self.arp_table.keys():
                print("New device is requiring IP address")
                new_available_ip_address = self.find_available_ip_address()
                print("Device ", mac_address, " is granted of ", new_available_ip_address, " ip address")
                self.arp_table[mac_address] = new_available_ip_address
                
            
            self.dhcp_sock.sendto(pickle.dumps(Packet(
                self.sim.get_gateway_recv_mac(),
                pkt.get_source_mac(), 
                self.sim.get_gateway_recv_ip(),
                pkt.get_source_ip(),
                self.arp_table[pkt.get_source_mac()]
            )) , address)


class Gateway:
    DHCP_PORT = 1075
    devices = {} # {ip_address: measurements}

    def __init__(self):
        self.sim = Simulation()

        self.rcv_sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM) # socket per invio delle misurazioni
        self.dhcp_sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

        self.dhcp_sock.bind(nc.dhcp_address)
        self.rcv_sock.bind(nc.gateway_address) 

        self.dhcp = SimpleDhcp(self.dhcp_sock)
        self.dhcp.start()  

    def get_rcv_ip_address(self):
        return self.sim.get_gateway_recv_ip()

    def get_udp_sock(self):
        return self.rcv_sock
    
    def get_devices(self):
        return self.devices

    def send_data_to_server(self):
        try:
            server_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
            server_socket.connect(nc.server_address)
            print("SENDING DEVICES DATA TO SERVER")
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
        utils.print_pkt_size(message)
        server_socket.close()
        
        pkt = pickle.loads(message)

        utils.print_packet_header(pkt, "SERVER")
        
        print("Server answer:", pkt.get_payload())
        utils.print_divider()
        print()
        self.clear_measurments()
    
    def clear_measurments(self):
        self.get_devices().clear()
    
    
    def send_answer(self, address, pkt, message):
        self.get_udp_sock().sendto(
            pickle.dumps(Packet(self.sim.get_gateway_recv_mac(),
                pkt.get_source_mac(),
                self.sim.get_gateway_recv_ip(),
                pkt.get_source_ip(),
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
        print("Gateway waiting to receive data from devices...\n")
        data, real_address = gateway.get_udp_sock().recvfrom(1024)
        utils.print_pkt_size(data)
        arrival_time = time.time_ns()
        
        pkt = pickle.loads(data)
        utils.print_divider()
        utils.print_packet_header(pkt, "DEVICE")
        time_for_receipt = arrival_time - pkt.get_sending_time()
        #Effettuiamo controllo se indirizzo ip del gateway ip coincide con quello attuale corretto
        if pkt.get_destination_ip() == gateway.get_rcv_ip_address():
            print("Time to receive this UDP datagram: ", time_for_receipt, "ns")
            # controllo che non si tratti di misurazioni gia inviate
            if pkt.get_source_ip() not in gateway.get_devices().keys():
                gateway.get_devices()[pkt.get_source_ip()] = pkt.get_payload()
            else:
                print("Discarding, this device already sent data")
                print("Waiting for other devices...\n")
            utils.print_divider()
            # invio conferma di ricezione al device
            gateway.confirm_reception(real_address, pkt)
            # non appena ho ricevuto le misurazioni dagli n device invio
            # i dati al server    
            n=4
            if (len(gateway.get_devices().keys())) == n:
                gateway.send_data_to_server()
        else:
            gateway.discard_reception(real_address, pkt)


if __name__ == '__main__':
    main()