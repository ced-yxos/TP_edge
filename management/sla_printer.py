import redis, json

with open('data.json', 'r') as file:
    data = json.load(file)

redis_host = data["master_ip"]
redis_port = 6380

r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

while True:
	keys = r.keys("*")
	for item in keys:
		print(item, ":",r.get(item))

