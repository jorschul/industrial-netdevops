# -*- coding: utf-8 -*-
#
# NETCONF Webex Bot
# Joerg Schultz / jorschul, Cisco Systems, July 2020
# Apache License 2.0
#
from webexteamsbot import TeamsBot
import json
from ncclient import manager
import xmltodict

# Retrieve required details from environment variables
bot_email = "poliber@webex.bot"
bot_token = "NDI1M2VkM2UtNjE0MC00MTcwLTk4NzEtNDg2ZDI1MzIzMjA5MWMyMDYwYTItYTA0_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"
bot_url = "https://021b6b0f6b41.ngrok.io" #try with ngrok.io
bot_app_name = "poc-poliber"

m = manager.connect(host="10.49.232.51", port=830, username="cisco", password="cisco", hostkey_verify=False)

# Create a Bot Object
bot = TeamsBot(
    bot_app_name,
    teams_bot_token=bot_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
)

# The bot returns the hostname and IOS version of the device
def getinfo(incoming_msg):
    netconf_reply = m.get_config(source='running')
    netconf_data = xmltodict.parse(netconf_reply.xml)
    return "Hostname: {}, IOS Version: {}".format(netconf_data["rpc-reply"]["data"]["native"]["hostname"],netconf_data["rpc-reply"]["data"]["native"]["version"])

# The bot returns all interfaces of the device
def getallinterfaces(incoming_msg):
    filter = '''
    <filter>
          <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"></interfaces>
      </filter>
    '''
    netconf_reply = m.get_config(source='running', filter=filter)
    netconf_data = xmltodict.parse(netconf_reply.xml)
    msg = ""
    for x in netconf_data["rpc-reply"]["data"]["interfaces"]["interface"]:
        msg = msg + "* Interface: {} - enabled: {} \n ".format(x["name"], x["enabled"])
    return msg

# Enable or disable the interface of FastEthernet 4
# depends on the user input
def change_interface4(incoming_msg):
    config = '''
        <config>
              <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                    <name>FastEthernet0/0/4</name>
                    <enabled>true</enabled>
                </interface>
              </interfaces>
          </config>
        '''
    config_dict = xmltodict.parse(config)

    # most basic differentiation of the user's command.
    if incoming_msg.text == "/changeint4 enable":
        netconf_reply = m.edit_config(target='running', config=config)
        return "Int4 was successfully enabled."
    elif incoming_msg.text == "/changeint4 disable":
        config_dict["config"]["interfaces"]["interface"]["enabled"] = "false"
        config = xmltodict.unparse(config_dict)
        netconf_reply = m.edit_config(target='running', config=config)
        return "Int4 was successfully disabled."
    else:
        return "Wrong command, please try again."

if __name__ == "__main__":
    # Add new commands to the box.
    bot.add_command("/getinfo", "Get basic device information", getinfo)
    bot.add_command("/getallinterfaces", "Get information from all interfaces", getallinterfaces)
    bot.add_command("/changeint4", "disable or enable Interface 4: e.g. /changeint4 disable", change_interface4)
    bot.remove_command("/echo")
    bot.set_help_message("Welcome to the PoC Polizei Berlin Bot! You can use the following commands:\n")

    # Run Bot
    bot.run(host="0.0.0.0", port=5000)
