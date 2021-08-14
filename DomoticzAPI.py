import base64
import hashlib
import requests
import re
import socket


class DomoticzAPI:
    DISARMED = 0
    ARM_HOME = 1
    ARM_AWAY = 2
    UNKNOWN = 3

    LOCKED = "0"
    UNLOCKED = "1"

    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.url = "http://" + hostname + ":" + port + "/json.htm"
        # id:passwd
        usrPass = username + ":" + password
        b64Val = base64.b64encode(usrPass.encode("UTF-8"))
        self.headers = {
            "Authorization": "Basic " + b64Val.decode("utf-8")
        }

    def getAlarmStatus(self):
        querystring = {"type": "command", "param": "getsecstatus"}
        response = requests.request("GET", self.url, data="", headers=self.headers, params=querystring)
        if response.ok:
            jsonResponse = response.json()
            return {"ok": True, "status": jsonResponse['secstatus'] }
        else:
            return {"ok": False}

    def setAlarmStatus(self, status, alarmPassword):
        hashedPassword = hashlib.md5(alarmPassword.encode("UTF-8")).hexdigest()
        querystring = {"type": "command", "param": "setsecstatus", "secstatus": status,
                       "seccode": hashedPassword}
        response = requests.request("GET", self.url, data="", headers=self.headers, params=querystring)
        if response.ok:
            jsonResponse = response.json()
            if jsonResponse['status'] == "OK":
                return {"ok": True}
            else:
                return {"ok": False, "message": self.translateMessage(jsonResponse['message'])}
        else:
            return {"ok": False, "message": "Unknown error"}

    def toggleAlarmStatus(self, alarmPassword):
        response = self.getAlarmStatus()

        if response['ok']:
            status = response['status']
            if (status == self.ARM_AWAY):
                status = self.DISARMED
            elif (status == self.DISARMED):
                status = self.ARM_AWAY

            result = self.setAlarmStatus(status, alarmPassword)
            return result

        else:
            return False

    def getDevices(self):
        querystring = {"type": "devices", "filter": "all", "used": "true", "order": "Name"}
        response = requests.request("GET", self.url, data="", headers=self.headers, params=querystring)
        if response.ok:
            devices = []
            jsonResponse = response.json()
            for device in jsonResponse["result"]:
                if device["SwitchType"] == "Door Lock":
                    # compute names
                    name = device["Name"]
                    try:
                        shortName = re.search('\((.+?)\)', name).group(1)
                    except AttributeError:
                        shortName = ''

                    # compute status
                    status = device["Status"]
                    if status == "Locked":
                        newStatus = self.LOCKED
                    else:
                        newStatus = self.UNLOCKED

                    devices.append({"name": shortName, "status": newStatus})
            myResponse = {"ok": True, "devices": devices}
        else:
            myResponse = {"ok": False}

        return myResponse

    def translateMessage(self, text):
        if text == "WRONG CODE":
            return "MAUVAIS CODE"
        else:
            return text

    def isAccessible(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.hostname, int(self.port)))
            s.shutdown(2)

            response = self.getAlarmStatus()
            if response['ok']:
                return True
            else:
                return False
        except:
            return False