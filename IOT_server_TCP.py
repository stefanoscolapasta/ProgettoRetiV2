import socket as sk
import pickle, time
from IOT_device_UDP import Measurement

class TcpServer:

    def __init__(self):
        self.server_port = 3001
        self.server_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.server_socket.bind(('localhost', self.server_port))
        self.server_socket.listen(1)
        self.gateway_ip_address = "10.10.10.1"

    def get_tcp_sock(self):
        return self.server_socket

    def close_server_socket(self):
        self.server_socket.close()

    def get_correct_gateway_ip_address(self):
        return self.gateway_ip_address

def main():

    server = TcpServer()

    while True:
        print ('Ready to serve...')
        connection_socket, addr = server.get_tcp_sock().accept()
        print("SERVER ACCEPTING CONNECTION FROM ", addr)
        print("Waiting to receive message")
        
        try:
            message = connection_socket.recv(1024)
            arrival_time = time.time_ns()       
            sender_ip_address, time_of_sending, data = pickle.loads(message)
            time_for_receipt = arrival_time - time_of_sending
            print("Time to receive data from gateway over a TCP connection: ", time_for_receipt, "ns")
            if sender_ip_address == server.get_correct_gateway_ip_address():
                print("Data received from GATEWAY")

                for address in data.keys():
                    print("\n\n--------------------------")
                    print("address: ", address)
                    print("MEASUREMENTS\n")
                    for measure in data[address]:
                        print(measure.to_string())
                    print("--------------------------\n\n")
                    
                connection_socket.send("Mesurement received".encode("utf-8"))
            else:
                print("Permission denied")
                connection_socket.send("Were you looking for this IP_address?".encode("utf-8"))
        except Exception as error:
            print(error)
        
        connection_socket.close()


if __name__ == '__main__':
    main()