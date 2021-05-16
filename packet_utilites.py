def create_packet(ethernet_header, IP_header, message):
    return ethernet_header + IP_header + message

def create_ethernet_header(source_mac, destination_mac):
    return source_mac + destination_mac

def create_ip_header(source_ip, destination_ip):
    return source_ip + destination_ip

def read_ethernet_header(packet):
    return (packet[0:17], packet[17:34])

def read_ip_header(packet):
    return (packet[34:45], packet[45:56])

def read_message(packet):
    return (packet[56:])
    
