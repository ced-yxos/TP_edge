import socket
import struct
import requests, json

with open('data.json', 'r') as file:
    detail = json.load(file)

#How to know edge server IP adress
def ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
    s.close()

mcast_grp = "224.1.1.1"
mcast_port = 5004

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind(('', mcast_port))
mreq = struct.pack("4sl", socket.inet_aton(mcast_grp), socket.INADDR_ANY)

sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

while True:
    print(sock.recv(10240).decode())
    print("Applying process engaged")
    data = {"ip":ip()}
    resp = requests.get(url="http://"+detail["master_ip"]+":7000/migrate", json=data)
