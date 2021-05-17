import socket as sk
import pickle, time
from IOT_device_UDP import Measurement
from IOT_packet import Packet
from IOT_simulation import Simulation

class TcpServer:

    def __init__(self):
        self.sim = Simulation()
        self.server_port = 3001
        self.server_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.server_socket.bind(('localhost', self.server_port))
        self.server_socket.listen(1)

    def get_tcp_sock(self):
        return self.server_socket

    def close_server_socket(self):
        self.server_socket.close()

    def get_correct_gateway_ip_address(self):
        return self.sim.get_gateway_send_ip()

def main():
    simulation = Simulation()
    server = TcpServer()
    while True:
        print ('Ready to serve...')
        connection_socket, addr = server.get_tcp_sock().accept()
        print("SERVER ACCEPTING CONNECTION FROM ", addr)
        print("Waiting to receive message")
        
        try:
            message = connection_socket.recv(1024)
            arrival_time = time.time_ns()      
            pkt = pickle.loads(message)
            print(pkt.to_string())
            time_for_receipt = arrival_time - pkt.get_sending_time()
            print("Time to receive data from gateway over a TCP connection: ", time_for_receipt, "ns")
            # controllare destination_ip
            if pkt.get_source_ip() == server.get_correct_gateway_ip_address():
                connection_socket.send(
                    pickle.dumps(Packet(simulation.get_server_mac(),
                        simulation.get_gateway_send_mac(),
                        simulation.get_server_ip(),
                        simulation.get_gateway_send_ip(),
                        "Meausurements receiceived"    
                    )
                ))
                print("Data received from GATEWAY")
                data = pkt.get_payload()
                for address in data.keys():
                    for measure in data[address]:
                        print(address,"-",measure.get_time_of_measurement(),"-",measure.get_temperature(),"-",measure.get_humidity())
                    print("--------------------------\n\n")    
            else:
                print("Permission denied")
                connection_socket.send(
                    pickle.dumps(Packet(simulation.get_server_mac(),
                        simulation.get_gateway_send_mac(),
                        simulation.get_server_ip(),
                        simulation.get_gateway_send_ip(),
                        "Were you looking for this IP_address?"    
                    )
                ))
        except Exception as error:
            print(error)
        
        connection_socket.close()


if __name__ == '__main__':
    main()