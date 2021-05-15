import socket as sk
import pickle
from IOT_device_UDP import Measurement

server_port = 3001
server_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
server_socket.bind(('',server_port))
server_socket.listen(1)
print ('Server ready to receive connections:',server_port)
while True:
    print ('Ready to serve...')
    connection_socket, addr = server_socket.accept()
    message = connection_socket.recv(1024)
    data = pickle.loads(message)

    for address in data.keys():
        print("\n\n--------------------------")
        print("address: ", address)
        print("MEASUREMENTS\n")
        for measure in data[address]:
            print(measure.to_string())
        print("--------------------------\n\n")
    connection_socket.send("Mesurement received".encode())
    connection_socket.close()

serverSocket.close()
connection_socket.close()
sys.exit() ## Termina il programma dopo aver inviato i dati corrispondenti