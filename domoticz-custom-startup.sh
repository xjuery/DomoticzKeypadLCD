#! /bin/bash

BASE_GPIO_PATH=/sys/class/gpio

exportGPIO()
{
  if [ ! -e $BASE_GPIO_PATH/gpio$1 ]; then
    # Export GPIO
    echo "$1" > $BASE_GPIO_PATH/export
    chmod 777 -R $BASE_GPIO_PATH/gpio$1

    # Set GPIO direction
    echo "$2" > $BASE_GPIO_PATH/gpio$1/direction

    # Invert GPIO (1 is closed by default and 0 is opened by default)
    #      Example: echo 1 > $BASE_GPIO_PATH/gpio17/active_low
    echo 1 > $BASE_GPIO_PATH/gpio$1/active_low
  fi
}

# List of exported GPIOs
exportGPIO 26 in
exportGPIO 12 in
exportGPIO 13 in

# Launch Domoticz
/home/pi/domoticz/domoticz -www 8080 -sslwww 443

