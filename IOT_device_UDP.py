import socket as sk
import time, pickle, os, random
from datetime import datetime
from udp_datagram import UdpDatagram

gateway_mac = "10:AF:CB:EF:19:CF"

class Device:

    DHCP_PORT = 1075
    GATEWAY_PORT = 6001
    daily_measurements = []
    maximum_number_of_measurements_to_be_sent = 5

    def __init__(self, mac_address):
        self.log_filename = "DailyDeviceLog_" + str(mac_address) + ".json" 
        self.udp_sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.gateway_address = ('localhost', self.GATEWAY_PORT)
        self.dhcp_address = ('localhost', self.DHCP_PORT)
        self.mac_address = mac_address
        # richiesta di un indirizzo ip dal dhcp
        self.ip_address, self.gateway_ip = self.retrieve_address_from_dhcp_server()
        print(self.ip_address)
        self.create_file()

    def retrieve_address_from_dhcp_server(self):
        self.udp_sock.sendto(str(self.mac_address).encode('utf8'), self.dhcp_address)
        data, server = self.udp_sock.recvfrom(4096)
        if data:
            ip_data = data.decode('utf8').split("_")
            return (ip_data[0], ip_data[1])
        return ''

    def close_socket(self):
        self.udp_sock.close()

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
        print("Device is sending data")
        starting_time = time.perf_counter_ns()
        
        self.udp_sock.settimeout(2)
        received = False
        while not received:
            try:
                self.udp_sock.sendto(pickle.dumps((self.ip_address, self.gateway_ip, starting_time, self.daily_measurements)), self.gateway_address)
                self.udp_sock.settimeout(2)
                data, gateway_address = self.udp_sock.recvfrom(4096) # attesa di conferma da parte del gateway
                if data:
                    received = True
            except sk.timeout:
                print("Timeout occurred, trying again...")
        time.sleep(2)
        if data:
            print("Server(", gateway_address, ") answer: ", data.decode('utf8'))
        # after sending data I reset the dictionary to not keep in ram useless data
        self.daily_measurements.clear()    

    def create_file(self):
        open(str(self.log_filename), 'w').close()

class Measurement:
    def __init__(self, time, temperature, humidity):
        self.time = time
        self.temperature = temperature
        self.humidity = humidity

    def get_time_of_measurement(self):
        return self.time

    def get_temperature(self):
        return self.temperature

    def get_humidity(self):
        return self.humidity

    def to_string(self):
        return str(
            "\nTIME_OF_MEASUREMENT: " + str(self.get_time_of_measurement()) + 
            "\nTEMPERATURE: " + str(self.get_temperature()) + 
            "\nHUMIDITY: " + str(self.get_humidity())
            )

class Environment:
    def get_current_measurement(self):
        random_temperature = random.randrange(-15,45)
        random_humidity = random.randrange(0,100)
        return Measurement(str(datetime.now()), random_temperature, random_humidity)

def main():
    current_environment = Environment()
    device_mac_address = str(input("Insert devices MAC_ADDRESS: "))
    device = Device(device_mac_address)
    while True:
        print("Adding new measurement")
        device.add_new_measurement(current_environment.get_current_measurement())
        time.sleep(1)


if __name__ == '__main__':
    main()
