#!/usr/bin/env python3

import RPi.GPIO as GPIO
import Keypad
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from DomoticzAPI import DomoticzAPI
import argparse

import hashlib

# KeyPad parameters
keypadRows = 4
keypadColumns = 4
keys =  [   '1','2','3','A',
            '4','5','6','B',
            '7','8','9','C',
            '*','0','#','D'     ]
rowsPins = [12,16,18,22]
columnsPins = [19,15,13,11]

# I2C Addresses
PCF8574_address = 0x27
PCF8574A_address = 0x3F

# Init PCF8574 GPIO
try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
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

def loop(domoticzUsername, domoticzPassword):
    domoticz = DomoticzAPI("192.168.1.23", "8080", domoticzUsername, domoticzPassword)

    keypadBuffer = ""
    keypad = Keypad.Keypad(keys,rowsPins,columnsPins,keypadRows,keypadColumns)
    keypad.setDebounceTime(50)

    # LCD Backlight
    mcp.output(3,1)

    # Init LCD
    lcd.begin(16,2)
    lcd.setCursor(0,0)

    while(True):
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
                domoticz.setAlarmStatus(domoticz.ARM_AWAY, keypadBuffer)
                keypadBuffer = ""
            else:
                # otherwise display * 
                if( keypadBuffer == ""):
                    lcd.clear()             
                    lcd.setCursor(0,0)
                keypadBuffer = keypadBuffer + key
                myPrint("*")
                
            
if __name__ == '__main__':

    my_parser = argparse.ArgumentParser(description='List the content of a folder')
    my_parser.add_argument('username',
                           metavar='username',
                           type=str,
                           help='username')
    my_parser.add_argument('password',
                           metavar='password',
                           type=str,
                           help='password')

    # Execute the parse_args() method
    args = my_parser.parse_args()

    try:
        loop(args.username, args.password)
    except KeyboardInterrupt:
        GPIO.cleanup()
        lcd.clear()
