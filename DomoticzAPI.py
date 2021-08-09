import base64
import hashlib
import requests


class DomoticzAPI:
    DISARMED = 0
    ARM_HOME = 1
    ARM_AWAY = 2
    UNKNOWN = 3

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
