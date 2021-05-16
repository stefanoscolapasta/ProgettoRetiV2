import socket as sk
import pickle
from IOT_device_UDP import Measurement

class TcpServer:

    def __init__(self):
        self.server_port = 3001
        self.server_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.server_socket.bind(('localhost', self.server_port))
        self.server_socket.listen(1)

    def get_tcp_sock(self):
        return self.server_socket

    def close_server_socket(self):
        self.server_socket.close()

def main():

    server = TcpServer()

    while True:
        print ('Ready to serve...')
        connection_socket, addr = server.get_tcp_sock().accept()
        print("SERVER ACCEPTING CONNECTION FROM ", addr)
        print("Waiting to receive message")
        
        try:
            message = connection_socket.recv(1024)
            data = pickle.loads(message)

            print("Data received from GATEWAY")

            for address in data.keys():
                print("\n\n--------------------------")
                print("address: ", address)
                print("MEASUREMENTS\n")
                for measure in data[address]:
                    print(measure.to_string())
                print("--------------------------\n\n")

        except Exception as error:
            print(error)

        connection_socket.send("Mesurement received".encode())
        connection_socket.close()


if __name__ == '__main__':
    main()