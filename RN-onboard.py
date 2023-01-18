#!/usr/bin/env python3

import prisma_sase
import json
import yaml
import argparse
import PushConfig
from time import sleep

#URLs
ike_gw_url="https://api.sase.paloaltonetworks.com/sse/config/v1/ike-gateways?folder=Remote Networks"
ipsec_tunnel_url="https://api.sase.paloaltonetworks.com/sse/config/v1/ipsec-tunnels?folder=Remote Networks"
RN_url="https://api.sase.paloaltonetworks.com/sse/config/v1/remote-networks?folder=Remote Networks"

#Push Config to controller
def push_config():
    PushConfig.push_candidate_config(["Remote Networks"], "push to Remote Networks", sdk)
    sleep(10)

def sdk_login_to_controller(filepath):
    with open(filepath) as f:
        client_secret_dict = yaml.safe_load(f)
        client_id = client_secret_dict["client_id"]
        client_secret = client_secret_dict["client_secret"]
        tsg_id_str = client_secret_dict["scope"]
        tsg = tsg_id_str.split(":")[1]
        #print(client_id, client_secret, tsg)

    global sdk 
    sdk = prisma_sase.API(controller="https://sase.paloaltonetworks.com/", ssl_verify=False)
   
    sdk.interactive.login_secret(client_id, client_secret, tsg)
    print("--------------------------------")
    print("Script Execution Progress: ")
    print("--------------------------------")
    print("Login to TSG ID {} successful".format(tsg))
    
   
#Reading config from .json file
def read_config(filename):
    with open(filename) as json_file:
        dataList = json.load(json_file)
    #print(dataList)
    return dataList

#Posting config
def post_config(url, payload):
    resp = sdk.rest_call(url=url, data=payload, method="POST")
    #print(resp)


#Create IKE GW
def create_ike_gw():
    #print("Creating IKE")
    payload_list = read_config("RN-IKE.json")
    #conf = False
    for payload in payload_list:
        #if conf == False:
        post_config(ike_gw_url,payload)
        #conf = True
    print("Creation of IKE GW successful.")

#Create IPSec tunnel
def create_ipsec_tunnel():
    payload_list = read_config("RN-Tunnel.json")
    for payload in payload_list:
        post_config(ipsec_tunnel_url,payload)
       
    print("Creation of IPSec Tunnel successful.")

#Create RN
def create_RN():
    payload_list = read_config("RN.json")
    for payload in payload_list:
        post_config(RN_url,payload)
        
    print("Creation of RN successful.")

#Main script 
def go():
    parser = argparse.ArgumentParser(description='Onboarding the LocalUsers, Service Connection and Security Rules.')
    parser.add_argument('-t1', '--T1Secret', help='Input secret file in .yml format for the tenant(T1) .') 
     
    args = parser.parse_args()
    T1_secret_filepath = args.T1Secret

    #Pass the secret of 'from tenant' to login
    sdk1 = sdk_login_to_controller(T1_secret_filepath)
    
    create_ike_gw()
    create_ipsec_tunnel()
    create_RN()
    print("Push Config to the controller START.")
    push_config()
    print("Push Config to the controller END.")


if __name__ == "__main__":
    go()