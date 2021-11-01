#!/usr/bin/env python3


import argparse
import time
import socket
import RPi.GPIO as GPIO
import Keypad
from LCD2004 import LCD2004
from DomoticzAPI import DomoticzAPI

# KeyPad parameters
keypadRows = 4
keypadColumns = 4
keys =  [
            '1','2','3','A',
            '4','5','6','B',
            '7','8','9','C',
            '*','0','#','D'     
        ]
rowsPins = [12,16,18,22]
columnsPins = [19,15,13,11]
KEYPAD_IDLE_S = 15

# LCD VARIABLES
LCD_ROWS = 4
LCD_COLUMNS = 20

lcd = LCD2004(pin_rs=0, pin_e=2, pins_db=[4,5,6,7])

def getIp():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

def displayTitle(api, oldStatus):
    response = api.getAlarmStatus()

    if response["ok"]:
        status = response["status"]
        if status != oldStatus:
            if(status == api.ARM_HOME):
                title = "Alarme Activee"
                lcd.title(title, True, True)
            elif(status == api.ARM_AWAY):
                title = "Alarme Activee"
                lcd.title(title, True, True)
            else:
                title = "Alarme Desactivee"     
                lcd.title(title, True, False)
            
            
    else:
        title = "Erreur status alarme"
        lcd.clear()
        lcd.title(title, True, False)
        status = oldStatus
    
    return status

def displayDomoticzStatus(api):
    response = api.getDevices()
    row = 1

    if response['ok']:
        devices = response['devices']
        for i in range(0, len(devices)):
            device = devices[i]
            text = device["name"] + ' : ' + device["status"]
            if (i % 2) == 0:
                lcd.messagePos(text, 0, row, False)
            else:
                lcd.messagePos(text, LCD_COLUMNS-len(text), row, False)
                # Si l'index du devices est impair s'est qu'on est en bout de ligne donc on change
                row = row + 1
    else:
        lcd.messagePos("Err. Recup. Domoticz", None, row, True)

def loop(domoticzHostname, domoticzPort, domoticzUsername, domoticzPassword):
    domoticz = DomoticzAPI(domoticzHostname, domoticzPort, domoticzUsername, domoticzPassword)

    keypadBuffer = ""
    keypad = Keypad.Keypad(keys,rowsPins,columnsPins,keypadRows,keypadColumns)
    keypad.setDebounceTime(50)
    keypadMode = False

    # Init LCD
    lcd.begin(LCD_COLUMNS,LCD_ROWS)
    lcd.setCursor(0,0)
    lcd.clear()
    alarmStatus = ""

    while(True):
        # Check if Domoticz is up
        if not domoticz.isAccessible():
            lcd.clear()
            while( not domoticz.isAccessible() ):
                lcd.messagePos("En attente de", None, 0, True)
                lcd.messagePos("DOMOTICZ", None, 1, True)
                ipTitle = str(getIp())
                lcd.messagePos(ipTitle, None, 3, True)
            alarmStatus = ""
            lcd.clear()

        # Check current mode (keypad mode or info display mode)
        if( not keypadMode ):
            # if not in keypad mode then display alarm status and devices statuses
            alarmStatus = displayTitle(domoticz, alarmStatus)
            displayDomoticzStatus(domoticz)
        else:
            # If in keypad mode then check if a key has been typed within KEYPAD_IDLE_S seconds
            currentTime = time.time()
            if(currentTime > (keypadModeLastType+KEYPAD_IDLE_S)):
                # go back to the info display mode
                alarmStatus = ""
                keypadMode = False

        key = keypad.getKey()
        if(key != keypad.NULL):
            # Now check what has been typed
            keypadMode = True
            keypadModeLastType = time.time()
            # check if cancel ("C") or return ("D")
            if(key == "C"):
                # Clear the LCD screen
                lcd.clear()
                keypadBuffer = ""
            elif(key == "D"):   
                # Send Code to Domoticz
                lcd.clear()
                result = domoticz.toggleAlarmStatus(keypadBuffer)
                if not result['ok']:
                    lcd.clear()
                    lcd.messagePos(result['message'], None, 1, True)
                    time.sleep(2)
                    lcd.clear()
                    alarmStatus = ""
                keypadBuffer = ""
                keypadMode = False
            elif(key == "A"):
                # Display the RPI IP address
                lcd.title(" " * LCD_COLUMNS)
                ipTitle = str(getIp())
                lcd.title(ipTitle, True, False)
                time.sleep(KEYPAD_IDLE_S)
            else:
                # otherwise display * 
                if( keypadBuffer == ""):
                    codeTitle = "Saisie du code :"
                    lcd.clear()
                    lcd.title(codeTitle, True, False)
                    lcd.setCursor(3,2)
                keypadBuffer = keypadBuffer + key
                lcd.message("*")
                
            
if __name__ == '__main__':

    my_parser = argparse.ArgumentParser(description='Python module to connect LCD2004 and keypad to Domoticz')
    my_parser.add_argument('username',
                           metavar='username',
                           type=str,
                           help='Domoticz account username')
    my_parser.add_argument('password',
                           metavar='password',
                           type=str,
                           help='Domoticz account password')
    my_parser.add_argument('--hostname',
                           metavar='hostname',
                           type=str,
                           help='Domoticz hostname (localhost by default)',
                           default='localhost')
    my_parser.add_argument('--port',
                           metavar='port',
                           type=str,
                           help='Domoticz port (8080 by default)',
                           default='8080')

    # Execute the parse_args() method
    args = my_parser.parse_args()

    try:
        loop(args.hostname, args.port, args.username, args.password)
    except KeyboardInterrupt:
        GPIO.cleanup()
        lcd.clear()
