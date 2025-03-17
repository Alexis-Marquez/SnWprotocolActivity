import socket
import sys
import udt, packet, timer


def create_checksum(i, data):
    checksum = 0
    seq_bytes = i.to_bytes(4, 'little')
    string = data + seq_bytes
    for byte in string:
        checksum += byte

    return checksum.to_bytes(8, 'little')  # Ensure 8-byte checksum



def verify_checksum(i, checksum, data):
    return create_checksum(i, data) == checksum


def receive_file_GbN(file_path, sock):
    pass


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Enter port number to use: ")
    port = int(input())
    print("Enter protocol to use (GbN or SnW): ")
    protocol = input()
    print("Enter filename to save received file as: ")
    filename = input().strip()
    sock.bind(('localhost', port))

    if protocol == 'GbN':
        receive_file_GbN(filename, sock)
    elif protocol == 'SnW':
        receive_file_SnW(filename, sock)




def receive_file_SnW(output_filename, sock):
    expected_seq = 0
    print("Ready to receive data")
    with open(output_filename, "wb") as f:
        while True:
            pkt, addr = udt.recv(sock)
            seq, checksum, dataRcvd = packet.extract(pkt)

            if verify_checksum(seq, checksum, dataRcvd):
                if seq == expected_seq:
                    print(f"Server: Received seq {seq}, {len(dataRcvd)} bytes")

                    if dataRcvd == b"EOF":
                        print("Server: File transfer complete, closing connection.")
                        sock.close()
                        break

                    f.write(dataRcvd)
                    expected_seq = 1 - expected_seq

                else:
                    print(f"Server: Out of order packet {seq}, resending last ACK")

                acktosend = f"ACK - {seq}".encode()
                ackpkt = packet.make(seq, create_checksum(seq, acktosend),acktosend)
                udt.send(ackpkt, sock, addr)

    print("Server: File successfully saved as", output_filename)


if __name__ == "__main__":
    main()
