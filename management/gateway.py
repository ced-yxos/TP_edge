from fastapi import FastAPI

import requests

import time, os, re
import json

with open('data.json', 'r') as file:

    detail = json.load(file)


count = 0

def return_port(cmd_output: str):

    nodeport_match = re.search(r"NodePort:\s+<unset>\s+(\d+)/TCP", cmd_output)

    #Check for matches

    if nodeport_match:

        #Extract nodeport number

        nodeport_value = nodeport_match.group(1)

        print("La valeur NodePort est :", nodeport_value)

    else:

        print("No nodeport assigned")

    return nodeport_value





edge_delay=[]

client_response = {"edge_response":"","cloud_response":""}

api_response = {}

app = FastAPI()

edge_url = ""

cloud_url = ""





@app.post("/gateway")

async def decision(data: dict):
     global client_response
     global count
     global detail

     if count == 0:
         resp = requests.get(url=cloud_url+"/db_init", json={"db_ip":detail["master_ip"]})

     print (data)

     #real time communication

     edge_server_data={"front_distance":data["front_distance"],"rear_distance":data["rear_distance"]}

     t1=time.time()

     edge_response = requests.post(url=edge_url, json=edge_server_data)

     t2=time.time()

     print(f"Edge server delay {(t2-t1)*1000} ms")

     if edge_response.status_code == 200:

         client_response["edge_response"] = edge_response.json()

     else:

         print(f"Something wrong with edge server: Error with {edge_response.status_code}")



     #On the fly communication

     if data["details"] == "interested":

         cloud_response = requests.get(url=cloud_url+"/road_side")

         if cloud_response.status_code == 200:

             client_response["cloud_response"] = cloud_response.json()

         else:

             print(f"Something wrong with cloud server: Error with {cloud_response.status_code}")

     else:

         client_response["cloud_response"]=""

     #client response

     return client_response





@app.get("/init")

async def set_service_endpoint(data: dict):

    global edge_url

    global cloud_url

    edge_url = data["edge_endpoint"]

    cloud_url = data["cloud_endpoint"]

    print(f"{edge_url} {cloud_url}")

