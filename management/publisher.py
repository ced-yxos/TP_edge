import redis 
import random
import time, json

with open('data.json', 'r') as file:
    data = json.load(file)

redis_host = data["master_ip"]
redis_port = 6379

input = []

r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

def simulate_temperature():
    return round(random.uniform(20, 30), 2)

while True:
    my_speed = simulate_temperature()
    # t1 = time.time()
    r.set("speed limitation",str(my_speed))
    r.set("occupation", random.randint(40,90))
    r.set("intersection", "free")
    r.set("crosswalk","free")
    print("Data Base status:")
    keys = r.keys("*")
    for item in keys:
        print(item, r.get(item))
    time.sleep(5)
    print("\n")
    # input.append(t1)
