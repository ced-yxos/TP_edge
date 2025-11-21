from fastapi import FastAPI
import redis
import uvicorn

data={}
#Data base stroring Trafic details
redis_host=""
redis_port=""
r = redis.StrictRedis()
app = FastAPI()


#Return Local trafic details
@app.get("/road_side")
async def send_trafic_details():
    global data
    keys = r.keys("*")
    for item in keys:
        data[item] = r.get(item)
    print(f"local area indication: {data}")
    return data

#Get database details
@app.get("/db_init")
async def get_db_adress(data: dict):
    global redis_host
    global redis_port
    global r
    redis_host = data["db_ip"]
    redis_port = "6379"
    r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
