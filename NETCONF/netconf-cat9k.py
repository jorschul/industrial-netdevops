# -*- coding: utf-8 -*-
#
# NETCONF getting started
# Joerg Schultz / jorschul, Cisco Systems, July 2020
# Apache License 2.0
#
from ncclient import manager
import xmltodict
import xml.dom.minidom
import lxml.etree as ET

#Input here the connection parameters for the IOS XE device
#Do not forget to enable NETCONF: device(config)#netconf-yang

# berlab-c9300  = 10.49.232.51
# homelab-c9300 = 192.168.178.111

m = manager.connect(host="10.49.232.51",
                    port=830,
                    username="cisco",
                    password="cisco",
                    hostkey_verify=False)

print("Connected.")

# get the running config in XML of the device
def get_running_config():
    netconf_reply = m.get_config(source='running')
    netconf_data = xml.dom.minidom.parseString(netconf_reply.xml).toprettyxml()
    print(netconf_data)

# get hostname and IOS version of the device - loading the whole config
# this should take longer
def get_hostname():
    netconf_reply = m.get_config(source='running')
    netconf_data = xmltodict.parse(netconf_reply.xml)
    print("IOS Version: {}".format(netconf_data["rpc-reply"]["data"]["native"]["version"]))
    print("Hostname: {}".format(netconf_data["rpc-reply"]["data"]["native"]["hostname"]))

# get hostname and IOS version of the device - using a filter
# this should be faster
def get_hostname_filter():
    filter = '''
    <filter>
          <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
              <hostname></hostname>
              <version></version>
          </native>
      </filter>
    '''
    netconf_reply = m.get_config(source='running', filter=filter)
    netconf_data = xmltodict.parse(netconf_reply.xml)
    print("IOS Version: {}".format(netconf_data["rpc-reply"]["data"]["native"]["version"]))
    print("Hostname: {}".format(netconf_data["rpc-reply"]["data"]["native"]["hostname"]))

# get capabilities / all supported YANG models of the device
def get_capabilities():
    for c in m.server_capabilities:
        print(c)

# change interface GigabitEthernet3
# 0 --> disable | 1 --> enable
def change_interface(user_selection):
  int_status = user_selection

  config = '''
      <config>
            <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
              <interface>
                  <name>GigabitEthernet3</name>
                  <enabled>false</enabled>
              </interface>
            </interfaces>
        </config>
      '''
  config_dict = xmltodict.parse(config)

  if int_status == int(1):
      config_dict["config"]["interfaces"]["interface"]["enabled"] = "true"
      config = xmltodict.unparse(config_dict)

  netconf_reply = m.edit_config(target='running', config=config)
  print("Did it work? {}".format(netconf_reply.ok))

# disable POE on switch
# for 0 --> disable add => <inline><never-choice/></inline>
# for 1 --> enable add => <inline><auto/></inline>

def poe_disable(user_selection):
  int_status = user_selection

  config = '''
    <config>  
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>1/0/3</name>
              <power xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-power">  
                <inline><never-choice/></inline>
              </power>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
      '''
  config_dict = xmltodict.parse(config)

  if int_status == int(1):
      config_dict["config"]["native"]["interface"]["name"]["power"]["inline"] = "auto"
      config = xmltodict.unparse(config_dict)
 
  netconf_reply = m.edit_config(target='running', config=config)
  print("Did it work? {}".format(netconf_reply.ok))

# enable POE on switch
# for 0 --> disable add => <inline><never-choice/></inline>
# for 1 --> enable add => <inline><auto/></inline>

def poe_enable(user_selection):
  int_status = user_selection

  config = '''
    <config>  
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>1/0/3</name>
              <power xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-power">  
                <inline><auto/></inline>
              </power>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
      '''
  config_dict = xmltodict.parse(config)

  if int_status == int(1):
      config_dict["config"]["native"]["interface"]["name"]["power"]["inline"] = "auto"
      config = xmltodict.unparse(config_dict)
 
  netconf_reply = m.edit_config(target='running', config=config)
  print("Did it work? {}".format(netconf_reply.ok))

# copy run start
def save_running_config():
    rpc_body = '''<cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>'''
    netconf_reply = m.dispatch(ET.fromstring(rpc_body)).xml 
    print("Did it work? {}".format(netconf_reply))

if __name__ == "__main__":
    while True:
        print("""


#    ____          ____           ____         _  _            _   ____               _  _            #
#   |  _ \  ___   / ___|         |  _ \  ___  | |(_) ____ ___ (_) | __ )   ___  _ __ | |(_) _ __      #
#   | |_) |/ _ \ | |      _____  | |_) |/ _ \ | || ||_  // _ \| | |  _ \  / _ \| '__|| || || '_ \     #
#   |  __/| (_) || |___  |_____| |  __/| (_) || || | / /|  __/| | | |_) ||  __/| |   | || || | | |    #
#   |_|    \___/  \____|         |_|    \___/ |_||_|/___|\___||_| |____/  \___||_|   |_||_||_| |_|    #
#                                                                                                     #

 

          POC Polizei Berlin - NETCONF/YANG on IOS XE devices! 
          Here are your options

              q: Quit
              1: Get running config
              2: Get hostname and IOS version (whole config)
              3: Get hostname and IOS version (filter used)
              4: Get all the YANG models from the device
              5: Disable POE on GigabitEthernet1/0/3
              6: Enable POE on GigabitEthernet1/0/3
              7: Set PXE boot variables (in progress)
              8: Unset PXE boot variables (in progress)
              9: Save the running-configuration
              """)
        var = input("Enter: ")
        if var == "q":
            exit()
        elif var == "1":
            get_running_config()
        elif var == "2":
            get_hostname()
        elif var == "3":
            get_hostname_filter()
        elif var == "4":
            get_capabilities()
        elif var == "5":
            poe_disable(0)
        elif var == "6":
            poe_enable(0)
        elif var == "7":
            change_interface(1)
        elif var == "8":
            change_interface(0)
        elif var == "9":
            save_running_config()
        else:
            print("Wrong input")
        print("Done.\n")
