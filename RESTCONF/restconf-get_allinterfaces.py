# -*- coding: utf-8 -*-
#
# Get all interfaces RESTCONF
# Joerg Schultz / jorschul, Cisco Systems, July 2020
# Apache License 2.0
#
import requests
import json

#Input here the connection parameters for the IOS XE device
#Do not forget to enable RESTCONF: device(config)#restconf
host = '110.49.232.51'
port = 443
username = 'cisco'
password = 'cisco'

def get_allinterfaces():
    url = "https://{h}:{p}/restconf/data/ietf-interfaces:interfaces".format(h=host, p=port)
    headers = { "Accept" : "application/yang-data+json"}
    response = requests.get(url, auth=(username, password),headers=headers, verify=False)
    print(json.dumps(response.json(),indent=4))

get_allinterfaces()