from scapy.all import *
import argparse

def extract_from_seq(pcap_file):
    packets = rdpcap(pcap_file)
    secret = ""
    for pkt in packets:
        if TCP in pkt and pkt[TCP].flags & 0x08:  # Ensure it's a PSH packet
            secret += chr(pkt[TCP].seq)
    print("Extracted message:", secret)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap", help="Input .pcap file")
    args = parser.parse_args()
    extract_from_seq(args.pcap)
