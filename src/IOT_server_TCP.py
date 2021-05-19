import socket as sk
import pickle, time, sys
from IOT_packet import Packet
from IOT_simulation import Simulation
from beautifultable import BeautifulTable
import utils
import signal

class TcpServer:

    def __init__(self):
        self.sim = Simulation()
        self.server_port = 3001
        self.server_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.server_socket.bind(('localhost', self.server_port))
        self.server_socket.listen(1)
        self.buffer_size = 4096

    def get_tcp_sock(self):
        return self.server_socket

    def close_server_socket(self):
        self.server_socket.close()

    def get_correct_gateway_ip_address(self):
        return self.sim.get_gateway_send_ip()

    def get_buffer_size(self):
        return self.buffer_size

server = TcpServer()

def main():
    global server
    simulation = Simulation()
    #interrompe l'esecuzione se da tastiera arriva la sequenza (CTRL + C) 
    try:
        while True:
            print ('Ready to serve...')
            connection_socket, addr = server.get_tcp_sock().accept()
            print ('Connection accepted')
            try:       
                print("Waiting to receive data...")
                message = connection_socket.recv(server.get_buffer_size())
                utils.print_pkt_size(message)
                arrival_time = time.time_ns()      
                pkt = pickle.loads(message) 
                time_for_receipt = arrival_time - pkt.get_sending_time()
                utils.print_divider()
                print("DATA RECEIVED")

                utils.print_packet_header(pkt, "GATEWAY")
                
                print("Time to receive data from gateway over a TCP connection: ", time_for_receipt, "ns")
                # controllare destination_ip
                if pkt.get_source_ip() == server.get_correct_gateway_ip_address():
                    
                    connection_socket.send(
                        pickle.dumps(Packet(simulation.get_server_mac(),
                            simulation.get_gateway_send_mac(),
                            simulation.get_server_ip(),
                            simulation.get_gateway_send_ip(),
                            "Measurements received"    
                        )
                    ))
                    
                    print("Data received from GATEWAY")
                    data = pkt.get_payload()

                    print_measurements(data)
                       
                else:
                    print("Permission denied")
                    connection_socket.send(
                        pickle.dumps(Packet(simulation.get_server_mac(),
                            simulation.get_gateway_send_mac(),
                            simulation.get_server_ip(),
                            simulation.get_gateway_send_ip(),
                            "Were you really looking for this IP_address?"    
                        )
                    ))
                utils.print_divider()
            except Exception as error:
                print(error)          
            connection_socket.close()
    except KeyboardInterrupt:
        pass

    server.close_server_socket()

def print_measurements(data):
    for address in data.keys():
        table = BeautifulTable()
        table.columns.header = ["Device IP Address", "Time of measurement", "Temperature", "Humidity"]
        
        for measure in data[address]:
            table.rows.append([address, measure.get_time_of_measurement(),  measure.get_temperature(),  measure.get_humidity()])
        
        print(table)
        print("\n\n") 



def signal_handler(signal, frame):
    global server
    print('Closing server (Ctrl+C pressed)')
    try:
        if server.get_tcp_sock():
            server.close_server_socket()
    finally:
        print("Exiting...")
        sys.exit(0)
        
signal.signal(signal.SIGINT, signal_handler)
if __name__ == '__main__':
    main()