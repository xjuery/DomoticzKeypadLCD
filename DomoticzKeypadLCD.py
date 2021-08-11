#!/usr/bin/env python3

import RPi.GPIO as GPIO
import Keypad
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from DomoticzAPI import DomoticzAPI
import argparse

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

# LCD VARIABLES
LCD_ROWS = 4
LCD_COLUMNS = 20

# I2C module Address
PCF8574_address = 0x27

# Init PCF8574 GPIO
try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    print ('Error with I2C Address !')
    exit(1)

lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

def myPrint(message):
    lcd.message( message )
    print(message, end="", flush=True)

def myPrintLn(message):
    lcd.message( message + '\n' )
    print(message, flush=True)

def displayTitle(api, oldStatus):
    status = api.getAlarmStatus()

    if(status != oldStatus):
        lcd.setCursor(0, 0)
        lcd.message(" " * LCD_COLUMNS)

        if(status == api.ARM_HOME):
            title = "Alarme Activee"
        elif(status == api.ARM_AWAY):
            title = "Alarme Activee"
        else:
            title = "Alarme Desactivee"

        half = int(len(title)/2)
        lcd.setCursor(int(LCD_COLUMNS/2) - half, 0)
        lcd.message(title)

    return status

def displayDomoticzStatus(api):
    devices = api.getDevices()
    row = 1

    for i in range(0, len(devices)):
        device = devices[i]
        text = device["name"] + ' : ' + device["status"]
        if (i % 2) == 0:
            lcd.setCursor(0, row)
            lcd.message(text) 
        else:
            lcd.setCursor(LCD_COLUMNS-len(text), row)
            lcd.message(text)

            # Si l'index du devices est impair s'est qu'on est en bout de ligne donc on change
            row = row + 1

def loop(domoticzHostname, domoticzPort, domoticzUsername, domoticzPassword):
    domoticz = DomoticzAPI(domoticzHostname, domoticzPort, domoticzUsername, domoticzPassword)

    keypadBuffer = ""
    keypad = Keypad.Keypad(keys,rowsPins,columnsPins,keypadRows,keypadColumns)
    keypad.setDebounceTime(50)
    keypadMode = False

    # LCD Backlight
    mcp.output(3,1)

    # Init LCD
    lcd.begin(20,4)
    lcd.setCursor(0,0)

    alarmStatus = ""

    while(True):
        alarmStatus = displayTitle(domoticz, alarmStatus)
        displayDomoticzStatus(domoticz)
        key = keypad.getKey()
        if(key != keypad.NULL):
            # check if cancel or return
            if(key == "C"):
                lcd.clear()
                lcd.setCursor(0,0)
                keypadBuffer = ""
            elif(key == "D"):   
                lcd.clear()             
                lcd.setCursor(0,0)
                myPrintLn("Entry:" + keypadBuffer)
                domoticz.toggleAlarmStatus(keypadBuffer)
                keypadBuffer = ""
            else:
                # otherwise display * 
                if( keypadBuffer == ""):
                    lcd.clear()             
                    lcd.setCursor(0,0)
                keypadBuffer = keypadBuffer + key
                myPrint("*")
                
            
if __name__ == '__main__':

    my_parser = argparse.ArgumentParser(description='Python module to connect LCD2004 and keypad to Domoticz')
    my_parser.add_argument('username',
                           metavar='username',
                           type=str,
                           help='username')
    my_parser.add_argument('password',
                           metavar='password',
                           type=str,
                           help='password')
    my_parser.add_argument('--hostname',
                           metavar='hostname',
                           type=str,
                           help='hostname',
                           default='localhost')
    my_parser.add_argument('--port',
                           metavar='port',
                           type=str,
                           help='port',
                           default='8080')

    # Execute the parse_args() method
    args = my_parser.parse_args()

    try:
        loop(args.hostname, args.port, args.username, args.password)
    except KeyboardInterrupt:
        GPIO.cleanup()
        lcd.clear()
