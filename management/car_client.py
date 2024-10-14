import random
import time
import requests
import redis, json

with open('data.json', 'r') as file:
    detail = json.load(file)

#Controller database connexion setup
redis_host=detail["master_ip"]
redis_port=6380
r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

data = {"front_distance":"0","rear_distance":"0","details": "uninterested"}
client_request={"authorized_delay":"250","services":["gateway", "edge", "cloud"]}

#proxy server address
response = requests.post(url="http://"+detail["master_ip"]+":7000/service_init", json=client_request)
gateway=response.json()
print(f"Proxy service details: {gateway['gateway']}")

#Ready to connect
time.sleep(5)

#Generate front and lateral ultrasonic sensor data
def distance_generator():
    i = random.randint(10,50)
    return i

#Interation with proxy server
def proxy_comm():
    global data
    global detail
    #Distance for edge service
    front_distance = distance_generator()
    rear_distance = distance_generator()
    data["front_distance"]= str(front_distance)
    data["rear_distance"]=str(rear_distance)

    #Request for environment details
    i = random.randint(10,17)
    if i >= 17 :
        data["details"]="interested"
    else:
        data["details"]="uninterested"

    #delay measure
    t1 = time.time()
    response = requests.post(url=gateway["gateway"], json=data)
    t2 = time.time()
    delay = (t2-t1)*1000

    #Feedbak on E2E delay
    r.set("observed_delay","{:.2f}".format(delay))
    if response.status_code == 200:
        instruction = response.json()
        print(f"Server response: {instruction}")
    else:
        print(f"Request failed with status {response.status_code}") 
    print("\n")


i = 0
try:
    while True:
        proxy_comm()
        time.sleep(5)
        i+=1
        if i%25==0:
            response=requests.post(url="http://"+detail["master_ip"]+":7000/update_delay",json={"new_delay":"365"})
            print(response.json())
        if i%15==0:
            response=requests.post(url="http://"+detail["master_ip"]+":7000/update_delay",json={"new_delay":"255"})
            print(response.json())
except(KeyboardInterrupt):
    print("Program ended !")
    r.flushall()

