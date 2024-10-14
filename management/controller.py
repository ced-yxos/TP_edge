from fastapi import FastAPI
import os, subprocess
import requests
import re
import time, json

with open('data.json', 'r') as file:
    data = json.load(file)

# Set up connectivity with the controller DB
redis_host = data["master_ip"]
redis_port = 6380
r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

i = 0

# Initialization commands
# Proxy initialization command
gateway_cmd = "docker run --name gateway -d -p 8000:8000 yxos/gateway"
# Cloud service deployment
cloud_cmd = "kubectl apply -f /home/user/documents/resources/cloud"
# Edge service deployment
edge_cmd = "kubectl apply -f /home/user/documents/resources/edge"

# Migration commands
node_1 = "kubectl apply -f /home/user/documents/resources/edge/edge_deployment_1.yaml"
node_2 = "kubectl apply -f /home/user/documents/resources/edge_deployment_2.yaml"

# Post-migration commands
close_1 = "kubectl delete -f /home/user/documents/resources/edge/edge_deployment_1.yaml"
close_2 = "kubectl delete -f /home/user/documents/resources/edge_deployment_2.yaml"

def return_port(cmd_output: str):
    nodeport_match = re.search(r"NodePort:\s+<unset>\s+(\d+)/TCP", cmd_output)
    # Check for matches
    if nodeport_match:
        # Extract nodeport number
        nodeport_value = nodeport_match.group(1)
        print("La valeur NodePort est:", nodeport_value)
    else:
        print("No nodeport assigned")
    return nodeport_value

# Available edge devices
edges = {"node_1": data["worker_1_ip"], "node_2": data["worker_2_ip"]}

# Setting up client API
app = FastAPI()

@app.post("/service_init")
async def service_deployment(requirements: dict):
    global i
    global data
    # Setting up SLA values
    r.set("expected_delay", requirements["authorized_delay"])

    # Deploying required services
    service_list = requirements["services"]
    print(service_list)
    for item in service_list:
        # Proxy deployment
        if item == "gateway":
            print("done")
            # try:
            # subprocess.run(gateway_cmd, shell=True, check=True)
            # print(f"Proxy deployed successfully !")
            # except subprocess.CalledProcessError as e:
            # print(f"Failed to deploy edge service : {e}")

        # Edge deployment
        elif item == "edge":
            os.system(edge_cmd)

        # Cloud deployment
        elif item == "cloud":
            os.system(cloud_cmd)

        else:
            print("Unable to process client request")

    # Get services port for cloud and edge app
    cmd_out = os.popen("kubectl describe service cloud-app-service")
    cloud_out = cmd_out.read()
    cmd_out.close()

    cmd_out = os.popen("kubectl describe service edge-app-service")
    edge_out = cmd_out.read()
    cmd_out.close()
    cloud_port = return_port(cloud_out)
    edge_port = return_port(edge_out)
    
    print(data)
    z = input()

    # Setting up endpoints
    cloud_endpoint = "http://"+data["worker_2_ip"]+":" + cloud_port
    edge_endpoint = "http://"+data["worker_1_ip"]+":" + edge_port + "/real_time"
    service_registry = {"edge_endpoint": edge_endpoint, "cloud_endpoint": cloud_endpoint}

    # Pushing endpoint into the proxy
    resp = requests.get(url="http://"+data["master_ip"]+":8000/init", json=service_registry)
    if resp.status_code == 200:
        print(f"All services deployed")
    else:
        print(f"Error with status code {resp.status_code}")

    # Initializing the current edge node in the service registry
    r.set("active_node", "node_1")
    return {"gateway": "http://"+data["master_ip"]+":8000/gateway"}

# Client can ask for service performance adjustment
@app.post("/update_delay")
async def sla_update(data: dict):
    r.set("expected_delay", data["new_delay"])
    print(f"Delay requirement updated")
    return {"message": "update successful"}

# Migration process
@app.get("/migrate")
async def edge_selection(info: dict):
    global i
    selected = info["ip"]
    active = r.get("active_node")

    if i % 2 == 0:
        i += 1
        print(f"first to respond: {selected}----active one {active}")
        if selected ==edges[active]:
            print(f"Can't migrate service! Best node is the one active {active}")
        else:
            if selected == edges["node_1"]:
                cmd_out = os.system(node_1)
                time.sleep(5)
                cmd_out = os.system(close_2)
                r.set("active_node", "node_1")
            else:
                cmd_out = os.system(node_2)
                time.sleep(5)
                cmd_out = os.system(close_1)
                r.set("active_node", "node_2")
    else:
        i += 1
    return None

    print(service_list)
    for item in service_list:
        # Proxy deployment
        if item == "gateway":
            print("done")
            # try:
            # subprocess.run(gateway_cmd, shell=True, check=True)
            # print(f"Proxy deployed successfully !")
            # except subprocess.CalledProcessError as e:
            # print(f"Failed to deploy edge service : {e}")

        # Edge deployment
        elif item == "edge":
            os.system(edge_cmd)

        # Cloud deployment
        elif item == "cloud":
            os.system(cloud_cmd)

        else:
            print("Unable to process client request")

    # Get services port for cloud and edge app
    cmd_out = os.popen("kubectl describe service cloud-app-service")
    cloud_out = cmd_out.read()
    cmd_out.close()

    cmd_out = os.popen("kubectl describe service edge-app-service")
    edge_out = cmd_out.read()
    cmd_out.close()
    cloud_port = return_port(cloud_out)
    edge_port = return_port(edge_out)
    
    print(data)
    z = input()

    # Setting up endpoints
    cloud_endpoint = "http://"+data["worker_2_ip"]+":" + cloud_port
    edge_endpoint = "http://"+data["worker_1_ip"]+":" + edge_port + "/real_time"
    service_registry = {"edge_endpoint": edge_endpoint, "cloud_endpoint": cloud_endpoint}

    # Pushing endpoint into the proxy
    resp = requests.get(url="http://"+data["master_ip"]+":8000/init", json=service_registry)
    if resp.status_code == 200:
        print(f"All services deployed")
    else:
        print(f"Error with status code {resp.status_code}")

    # Initializing the current edge node in the service registry
    r.set("active_node", "node_1")
    return {"gateway": "http://"+data["master_ip"]+":8000/gateway"}

# Client can ask for service performance adjustment
@app.post("/update_delay")
async def sla_update(data: dict):
    r.set("expected_delay", data["new_delay"])
    print(f"Delay requirement updated")
    return {"message": "update successful"}

# Migration process
@app.get("/migrate")
async def edge_selection(info: dict):
    global i
    selected = info["ip"]
    active = r.get("active_node")

    if i % 2 == 0:
        i += 1
        print(f"first to respond: {selected}----active one {active}")
        if selected ==edges[active]:
            print(f"Can't migrate service! Best node is the one active {active}")
        else:
            if selected == edges["node_1"]:
                cmd_out = os.system(node_1)
                time.sleep(5)
                cmd_out = os.system(close_2)
                r.set("active_node", "node_1")
            else:
                cmd_out = os.system(node_2)
                time.sleep(5)
                cmd_out = os.system(close_1)
                r.set("active_node", "node_2")
    else:
        i += 1
    return None

