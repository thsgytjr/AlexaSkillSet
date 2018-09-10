import boto3
import os
import socket
import time
access_key = "AKIAJKXX4U6AWUQIV5WQ"
access_secret = "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"
region = "us-east-1"
client = boto3.client('sqs', aws_access_key_id = access_key, aws_secret_access_key = access_secret, region_name = region)

MACHINE_HOSTNAME = socket.gethostname()
ENTPERISE_DASHBOARD_PORT = 1506
PORTAL_PORT = 1507
REGISTRY_PORT = 1528

QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/318645829848/AlexaScript"

START_ENTERPRISE_DASHBOARD = "sh ./CA/DevTest/bin/EnterpriseDashboard > /dev/null 2>&1 &"
START_PORTAL = "sh ./CA/DevTest/bin/Portal > /dev/null 2>&1 &"
START_REGISTRY = "sh ./CA/DevTest/bin/registry > /dev/null 2>&1 &"
STOP_ALL_SERVICES = "sh ./CA/DevTest/bin/stopdefservers.sh > /dev/null 2>&1 &"

KILL_ENTPERISE_DASHBOARD = "ps aux | grep -ie  EnterpriseDashboard | awk '{print $2}' | xargs kill -9"
KILL_PORTAL = "ps aux | grep -ie  portal | awk '{print $2}' | xargs kill -9"
KILL_REGISTRY = "ps aux | grep -ie  registry | awk '{print $2}' | xargs kill -9"

def start_stop_services(message):
    if message == 'EnterpriseDashboardOn':
        if check_running_services(MACHINE_HOSTNAME,ENTPERISE_DASHBOARD_PORT) == False:
            post_message(client,"Starting Enterprise Dashboard",QUEUE_URL)
            print("Starting Enterprise Dashboard")
            os.system(START_ENTERPRISE_DASHBOARD)
        else:
            print ("Enterprise Dashboard is already running")
            post_message(client,"Enterprise Dashboard is already running",QUEUE_URL)
    elif message =="EnterpriseDashboardOff":
        print("Stoping Enterprise Dashboard")
        os.system(KILL_ENTPERISE_DASHBOARD)
    elif message == "PortalOn":
        if check_running_services(MACHINE_HOSTNAME,PORTAL_PORT) == False:
            print("Starting portal")
            os.system(START_PORTAL)
            post_message(client,"Starting Portal",QUEUE_URL)
        else:
            post_message(client,"Portal is already running",QUEUE_URL)
    elif message == "PortalOff":
        print("Stoping Portal")
        os.system(KILL_PORTAL)
    elif message == "RegistryOn":
        if check_running_services(MACHINE_HOSTNAME,REGISTRY_PORT) == False:
            post_message(client,"Starting Registry",QUEUE_URL)
            print("Starting Registry")
            os.system(START_REGISTRY)
        else:
            print ("Registry is already running")
            post_message(client,"Registry is already running",QUEUE_URL)
    elif message == "RegistryOff":
        print("Stoping Registry")
        os.system(KILL_REGISTRY)
    elif message == "DidNotUnderstand":
        post_message(client,"Notable to start requested service",QUEUE_URL)
    elif message == "StopAllServices":
        print("Stopping All Services")
        os.system(KILL_ENTPERISE_DASHBOARD)
        os.system(KILL_PORTAL)
        os.system(KILL_REGISTRY)

def list_running_services(MACHINE_HOSTNAME):
    runningServices = []
    allServices = [ENTPERISE_DASHBOARD_PORT,PORTAL_PORT,REGISTRY_PORT]
    for item in allServices:
        if item == ENTPERISE_DASHBOARD_PORT and check_running_services(MACHINE_HOSTNAME,item)==True:
            runningServices.append("Enterprise Dashboard")
        elif item == PORTAL_PORT and check_running_services(MACHINE_HOSTNAME,item)==True:
            runningServices.append("Portal")
        elif item == REGISTRY_PORT and check_running_services(MACHINE_HOSTNAME,item)==True:
            runningServices.append("Registry")

    running_service_name = ', '.join(runningServices)
    if (running_service_name==""):
        running_services = "There are no services running"
    else:
        running_services = "Curretnly running " + running_service_name + " services"
    return running_services
    
def check_running_services(MACHINE_HOSTNAME,service_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((MACHINE_HOSTNAME,service_port))
    if result == 0:
       return True
    else:
        return False

def post_message(client, message_body, url):
    print("Posting message")
    response = client.send_message(QueueUrl = url, MessageBody= message_body)

def pop_message(client, url):
    response = client.receive_message(QueueUrl = url, MaxNumberOfMessages = 10)
     #last message posted becomes messages
    message = response['Messages'][0]['Body']
    receipt = response['Messages'][0]['ReceiptHandle']
    client.delete_message(QueueUrl = url, ReceiptHandle = receipt)
    return message

waittime = 1
client.set_queue_attributes(QueueUrl = QUEUE_URL, Attributes = {'ReceiveMessageWaitTimeSeconds': str(waittime)})
time_start = time.time()
while (time.time() - time_start < 600000):
        # print("Checking...")
        try:
                message = pop_message(client, QUEUE_URL)
                if (message == "listOfRunningServices"):
                    print(list_running_services(MACHINE_HOSTNAME))
                    post_message(client,list_running_services(MACHINE_HOSTNAME),QUEUE_URL)
                else:
                    start_stop_services(message)
        except:
                pass