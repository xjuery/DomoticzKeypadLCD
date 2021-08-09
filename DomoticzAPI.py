import base64
import hashlib
import requests
import re

class DomoticzAPI:
    DISARMED = 0
    ARM_HOME = 1
    ARM_AWAY = 2
    UNKNOWN = 3

    LOCKED = "Desactivé"
    UNLOCKED = "Activé"

    def __init__(self, hostname, port, username, password):
        self.url = "http://"+hostname+":"+port+"/json.htm"
        # id:passwd
        usrPass = username+":"+password
        b64Val = base64.b64encode(usrPass.encode("UTF-8"))
        self.headers = {
            "Authorization": "Basic "+b64Val.decode("utf-8")
        }

    def getAlarmStatus(self):
        querystring = {"type": "command", "param": "getsecstatus"}
        payload = ""
        response = requests.request("GET", self.url, data=payload, headers=self.headers, params=querystring).json()
        return response['secstatus']

    def setAlarmStatus(self, status, alarmPassword):
        hashedPassword = hashlib.md5(alarmPassword.encode("UTF-8")).hexdigest()

        querystring = {"type": "command", "param": "setsecstatus", "secstatus": status,
                       "seccode": hashedPassword}
        payload = ""
        requests.request("GET", self.url, data=payload, headers=self.headers, params=querystring)

    def toggleAlarmStatus(self, alarmPassword):
        status = self.getAlarmStatus()
        
        if(status == self.ARM_AWAY):
            status = self.DISARMED
        elif(status == self.DISARMED):
            status = self.ARM_AWAY
        
        hashedPassword = hashlib.md5(alarmPassword.encode("UTF-8")).hexdigest()

        querystring = {"type": "command", "param": "setsecstatus", "secstatus": status,
                       "seccode": hashedPassword}
        payload = ""
        requests.request("GET", self.url, data=payload, headers=self.headers, params=querystring)

    def getDevices(self):
        querystring = {"type": "devices", "filter": "all", "used": "true", "order": "Name"}

        response = requests.request("GET", self.url, data="", headers=self.headers, params=querystring).json()
        devices = []
        for device in response["result"]:
            if(device["SwitchType"] == "Door Lock"):
                # compute names
                name = device["Name"]
                try:
                    shortName = re.search('\((.+?)\)', name).group(1)
                except AttributeError:
                    shortName = ''

                # compute status
                status = device["Status"]
                if(status == "Locked"):
                    newStatus = self.LOCKED
                else:
                    newStatus = self.UNLOCKED

                devices.append({"name": shortName, "status": newStatus})

        return devices