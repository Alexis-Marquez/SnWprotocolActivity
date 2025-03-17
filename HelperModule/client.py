import socket
import sys
import time

from IPython.utils.timing import clock

import udt, packet
import timer as t

packets_sent = 0
packets_retransmitted = 0
transmission_time = 0

def create_checksum(i, data):
    checksum = 0
    seq_bytes = i.to_bytes(4, 'little')
    string = data + seq_bytes
    for byte in string:
        checksum += byte

    return checksum.to_bytes(8, 'little')  # Ensure 8-byte checksum



def verify_checksum(i, checksum, data):
    return create_checksum(i, data) == checksum



def send_file_GbN(file_path, sock, server_address):
    pass

def send_file_SnW(filename, sock, server_address):
    global packets_sent
    global packets_retransmitted
    global transmission_time

    mytimer = t.Timer(1)
    with open(filename, "rb") as f:
        i = 0

        while True:
            start_time = time.time()
            chunk = f.read(1000)
            if not chunk:
                break

            checksum = create_checksum(i, chunk)
            pkt = packet.make(i, checksum, chunk)

            ack_received = False
            while not ack_received:
                udt.send(pkt, sock, server_address)
                packets_sent += 1
                print(f"Client: Sent seq {i}, {len(chunk)} bytes")

                mytimer.start()
                while mytimer.running() and not mytimer.timeout():
                    try:
                        rcvpkt, addr = udt.recv(sock)
                        seq, checksum, dataRcvd = packet.extract(rcvpkt)

                        if seq == i and verify_checksum(seq, checksum, dataRcvd):
                            print(f"Client: Ack received for seq {seq}")
                            ack_received = True
                            mytimer.stop()
                        else:
                            print("Client: Incorrect ACK received")
                    except BlockingIOError:
                        continue

                if not ack_received:
                    print(f"Client: Timeout, resending seq {i}")
                    packets_retransmitted +=1
                    packets_sent += 1
                mytimer.stop()

            i = 1 - i

    eof_pkt = packet.make(i, create_checksum(i, b"EOF"), b"EOF")
    udt.send(eof_pkt, sock, server_address)
    print("Client: Sent EOF")
    end_time = time.time()
    transmission_time = end_time - start_time
    sock.close()

def main():

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)	 # making the socket non-blocking
    print("Enter port number to use: ")
    port = int(input())
    print("Enter protocol to use (GbN or SnW): ")
    protocol = input()
    server_address = ('localhost', port)
    print("Enter path of file to send")
    file_path = input()

    if protocol == 'GbN':
        send_file_GbN(file_path, sock, server_address)
    elif protocol == 'SnW':
        send_file_SnW(file_path,sock, server_address)
    print("Total packets sent: ", packets_sent)
    print("Total packets retransmitted: ", packets_retransmitted)
    print("Total transmission time: ", transmission_time/1000, " milliseconds")
if __name__ == "__main__":
    main()