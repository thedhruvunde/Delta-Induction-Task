#TO EMBED SECRET MESSAGE IN A PCAP FILE
from scapy.all import *
import argparse

def hide_message(message, output_pcap):
    packets = []
    for i, char in enumerate(message):
        seq_value = ord(char)
        # pkt = IP(dst="10.0.0.1")/TCP(sport=1234, dport=80, seq=ord(char))
        pkt = IP(dst="10.0.0.1")/TCP(sport=1234+i, dport=80, flags="PA", seq=seq_value) / Raw(load="X")
        # print(pkt)
        packets.append(pkt)

    wrpcap(output_pcap, packets)
    print(f"Hidden message written to '{output_pcap}' using IP ID field.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hide message in PCAP using IP ID field")
    parser.add_argument("message", help="Secret message to hide")
    parser.add_argument("output", help="Output PCAP file")
    args = parser.parse_args()
    hide_message(args.message, args.output)
