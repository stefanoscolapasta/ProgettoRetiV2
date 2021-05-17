import time
class Packet():
    def __init__(self, src_mac, dest_mac, src_ip, dest_ip, payload):
        self.source_MAC = src_mac
        self.destination_MAC = dest_mac
        self.source_IP = src_ip
        self.destination_IP = dest_ip
        self.payload = payload
        self.sending_time = time.time_ns()
    
    def get_source_ip(self):
        return self.source_IP

    def get_destination_ip(self):
        return self.destination_IP

    def get_source_mac(self):
        return self.source_MAC

    def get_destination_mac(self):
        return self.destination_MAC

    def get_payload(self):
        return self.payload

    def get_sending_time(self):
        return self.sending_time
    
    def to_string(self):
        return "IP[from:" + self.get_source_ip() + ",to:" + self.get_destination_ip() + "]\n" + "MAC[from:" + self.get_source_mac() + ",to:" + self.get_destination_mac() + "]\n" +  "PAYLOAD[" + str(self.get_payload()) + "]\n\n"