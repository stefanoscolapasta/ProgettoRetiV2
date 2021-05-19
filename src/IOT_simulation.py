class Simulation():
    def __init__(self):
        # per comunicazioni dai device al gateway
        self.gateway_recv_ip = "192.168.1.1"
        self.gateway_recv_mac = "10:AF:CB:EF:19:CF"
        # per comunicazioni dal gateway al server
        self.gateway_send_ip = "10.0.0.1"
        self.gateway_send_mac = "9B:AF:CB:EF:20:F0"
        self.server_ip = "10.0.0.2"
        self.server_mac = "F8:E2:BB:C1:D4:23"

    def get_gateway_recv_ip(self):
        return self.gateway_recv_ip

    def get_gateway_recv_mac(self):
        return self.gateway_recv_mac

    def get_gateway_send_ip(self):
        return self.gateway_send_ip

    def get_gateway_send_mac(self):
        return self.gateway_send_mac

    def get_server_ip(self):
        return self.server_ip

    def get_server_mac(self):
        return self.server_mac