import socket as sk
import time, pickle, os
import network_config as nc
from IOT_packet import Packet
from IOT_simulation import Simulation
from IOT_environment import Environment
import utils

class Device:
    daily_measurements = []
    maximum_number_of_measurements_to_be_sent = 6
    empty_payload = ""
    unassigned_ip = "0.0.0.0"

    def __init__(self, mac_address):
        self.sim = Simulation()
        self.log_filename = "DailyDeviceLog_" + str(mac_address).replace(":", "_") + ".json" 
        self.mac_address = mac_address
        # richiesta di un indirizzo ip dal dhcp
        print("Device requesting Ip address from DHCP server")
        self.ip_address = self.obtain_ip_address()
        print("Ip address received from DHCP server on gateway: ", self.ip_address)
        self.create_file()

    def obtain_ip_address(self):
        dhcp_request_socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

        dhcp_request_socket.sendto(pickle.dumps(Packet(
            self.mac_address, 
            self.sim.gateway_recv_mac,
            self.unassigned_ip, 
            self.sim.get_gateway_recv_ip(), 
            self.empty_payload
        )), nc.dhcp_address)

        data, server = dhcp_request_socket.recvfrom(1024)
        utils.print_pkt_size(data)
        pkt = pickle.loads(data)
        
        utils.print_packet_header(pkt, "DHCP SERVER")
        
        dhcp_request_socket.close()
        
        if data:
            return pkt.get_payload() 

        return self.unassigned_ip

    def add_new_measurement(self, measurement):
        self.daily_measurements.append(measurement)
        if os.path.exists(self.log_filename):
            with open(self.log_filename, 'a') as file:
                file.write(measurement.to_string())

        if len(self.daily_measurements) == self.maximum_number_of_measurements_to_be_sent:
            self.send_data()
            #To erase content from file
            open(self.log_filename, 'a').close()

    def send_data(self):
        print("\nDevice is sending data to GATEWAY...\n")
        # creo la socket e la richiudo non appena ho terminato l'invio dei dati
        # non impegnando inultimente le risorse allocate
        sending_socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)    
        received = False
        while not received:
            try:
                sending_socket.sendto(
                    pickle.dumps(Packet(self.mac_address,
                        self.sim.get_gateway_recv_mac(),
                        self.ip_address,
                        self.sim.get_gateway_recv_ip(),
                        self.daily_measurements)),
                    nc.gateway_address
                )
                sending_socket.settimeout(2)
                data, address = sending_socket.recvfrom(1024) # attesa di conferma da parte del gateway
                utils.print_pkt_size(data)
                if data:
                    pkt = pickle.loads(data)
                    utils.print_divider()
                    utils.print_packet_header(pkt, "GATEWAY")
                    received = True
                    print("Gateway answer:", pkt.get_payload())
                    utils.print_divider()
                    #empty print for spacing
                    print()

            except sk.timeout:
                print("Timeout occurred, trying again...")

        sending_socket.close()
        # after sending data I reset the dictionary to not keep in ram useless data
        self.daily_measurements.clear()    

    def create_file(self):
        open(str(self.log_filename), 'w').close()

def main():
    current_environment = Environment()
    device_mac_address = str(input("Insert devices MAC_ADDRESS: "))
    device = Device(device_mac_address)
    while True:
        print("Adding new measurement")
        device.add_new_measurement(current_environment.get_current_measurement())
        time.sleep(4) #una misurazione ogni 4 ore


if __name__ == '__main__':
    main()
