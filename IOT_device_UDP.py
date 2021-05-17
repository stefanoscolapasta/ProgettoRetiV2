import socket as sk
import time, pickle, os, random
from datetime import datetime
import network_config as nc
from IOT_packet import Packet
from IOT_simulation import Simulation

class Device:
    daily_measurements = []
    maximum_number_of_measurements_to_be_sent = 5

    def __init__(self, mac_address):
        self.sim = Simulation()
        self.log_filename = "DailyDeviceLog_" + str(mac_address) + ".json" 
        self.mac_address = mac_address
        # richiesta di un indirizzo ip dal dhcp
        self.ip_address, self.gateway_ip = self.obtain_ip_address()
        print(self.ip_address)
        self.create_file()

    def obtain_ip_address(self):
        dhcp_socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        dhcp_socket.sendto(str(self.mac_address).encode('utf8'), nc.dhcp_address)
        data, server = dhcp_socket.recvfrom(4096)
        dhcp_socket.close()
        if data:
            ip_data = data.decode('utf8').split("_")
            return (ip_data[0], ip_data[1])  
        return ''

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
        # creo la socket e la richiudo non appena ho terminato l'invio dei dati
        # non impegnando inultimente le risorse allocate
        gateway_socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)    
        received = False
        while not received:
            try:
                gateway_socket.sendto(
                    pickle.dumps(Packet(self.mac_address,
                        self.sim.get_gateway_recv_mac(),
                        self.ip_address,
                        self.sim.get_gateway_recv_ip(),
                        self.daily_measurements)),
                    nc.gateway_address
                )
                gateway_socket.settimeout(2)
                data, gateway_address = gateway_socket.recvfrom(4096) # attesa di conferma da parte del gateway
                pkt = pickle.loads(data)
                if data:
                    received = True
                    print("Gateway answer:",pkt.get_payload())
                    print()
            except sk.timeout:
                print("Timeout occurred, trying again...")
        gateway_socket.close()
        time.sleep(2)
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
    def __str__(self):
        return "measure(time: " + str(self.get_time_of_measurement()) + ", temp: " + str(self.get_temperature()) + ", hum: " + str(self.get_humidity()) + ")"

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
