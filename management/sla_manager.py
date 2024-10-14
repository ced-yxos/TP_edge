import redis
import requests
import time
import socket, json

with open('data.json', 'r') as file:
    data = json.load(file)

old = 0
#Setting up multicast server for migration trigger
group = "224.1.1.1"
port = 5004
#Hop restriction in network
ttl = 5
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
#trigger message 
msg = "Edge selection"

#Connexion to sla database
redis_host = data["master_ip"]
redis_port = 6380
r =  redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

#waiting to start
all_keys = []
i=0
while len(all_keys)!=2:
    all_keys = r.keys("*")
    if i == 0:
        print("Waiting for Contract to monitor")
        i+=1
print("New contract added. Monitoring in progress !")

count = 0
#Monitoring loop
while True:
    #Retrieve expected performances from client
    max_delay=float(r.get("expected_delay"))
    while r.get("observed_delay") == None:
    	if count == 0:
    		print("Waiting for QoE")
    		count+=1
    actual_delay=float(r.get("observed_delay"))

    #Comparison with expected values
    if actual_delay >= max_delay and old != actual_delay:
        print(f" desired delay: {max_delay} !=  observed delay: {actual_delay} ==> migration to new server:")
        #Trigger migration process
        sock.sendto(msg.encode(), (group, port))
        old = actual_delay
    else:
        print(f"QoE: {actual_delay}------SLA: {max_delay} ==> System performances Ok")
    time.sleep(2.5)
    

