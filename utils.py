# -*- coding: utf-8 -*-
from beautifultable import BeautifulTable

def print_packet_header(pkt, origin):
    table = BeautifulTable()
    table.columns.header = ["Source MAC", "Destination MAC", "Source IP", "Destination IP"]
    table.rows.append([pkt.get_source_mac(), pkt.get_destination_mac(),  pkt.get_source_ip(),  pkt.get_destination_ip()])
    print("RECEIVED PACKET HEADER FROM", origin)
    print(table)
    print("\n")
    
def print_divider():
    print("-"*80)