#! /bin/bash

BASE_GPIO_PATH=/sys/class/gpio

exportGPIO()
{
  if [ ! -e $BASE_GPIO_PATH/gpio$1 ]; then
    echo "$1" > $BASE_GPIO_PATH/export
    chmod 777 -R $BASE_GPIO_PATH/gpio$1
    echo "$2" > $BASE_GPIO_PATH/gpio$1/direction
  fi
}

exportGPIO 26 in
exportGPIO 12 in
exportGPIO 13 in


# Invert GPIO 17 (1 is closed and 0 is opened)
#echo 1 > $BASE_GPIO_PATH/gpio17/active_low
echo 1 > $BASE_GPIO_PATH/gpio26/active_low
echo 1 > $BASE_GPIO_PATH/gpio12/active_low
echo 1 > $BASE_GPIO_PATH/gpio13/active_low

/home/pi/domoticz/domoticz -www 8080 -sslwww 443

