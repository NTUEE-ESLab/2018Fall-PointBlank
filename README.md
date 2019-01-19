# PointBlank
## Introduction
### Overview
PointBlank is intended to be an advanced version of a presentation pointer. It utilizes a gyroscope combined with an accelerometer rather than visual light markers to determine the pointer's orientation. In addition, it has the ability to act as a magnifying glass or simulate a mouse, expanding the capability of presentation pointers.

### Modes
1. "Laser"  
   ![laser mode](https://drive.google.com/uc?id=1Z6dSoSBDCfaTY0aqWeR3gc14uwZ7pecu)
2. "Highlight"  
   ![highlight mode](https://drive.google.com/uc?id=1nmL9WG6JzVtWSaJk0aBSbOtc5kD3V-lJ)
3. "Magnify"  
   ![magnify mode](https://drive.google.com/uc?id=1DECowGI2Fo_dc-A5QnImuL0ytASUVZsP)
4. "Mouse"  
    The previous modes are meant for presentation, so their next/prev. slide buttons simulate DOWN and UP of the keyboard.
    In contrast, this mode doesn't draw anything on screen, but simulates left and right clicks of a mouse.

## Components
* Raspberry Pi
* Arduino Uno R3
* MPU-9250 (Gyro + Accelerometer + Compass)
* Analog five button keyboard module (such as the one shown below)
 ![button module image](https://ae01.alicdn.com/kf/HTB1jBkkxeOSBuNjy0Fdq6zDnVXaP/AD-Keyboard-Simulate-Five-Key-Module-Analog-Button-Sensor-Expansion-Board.jpg_640x640.jpg)
* Power bank
* A USB cable with switch (connecting Raspberry Pi to the Power Bank)

## Dependencies
### On PC
This part of the project is written in **python3**.
Please install the libraries [PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/installation.html) and [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/install.html).


**_Note:_** This project is tested on Ubuntu 16.04. For now, it is **not** compatible with Windows.

### On Raspberry Pi
You need to install BlueZ and enable Bluetooth Low Energy on Raspberry Pi by following this guide:
[BlueZ setup](https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation).

Please also make sure you have **python2** installed.

**_Note:_** This project is tested on Raspberry Pi 3 with Raspbian as OS.

## Usage
### Software Installation
1. Download the source codes to both the PC and the Raspberry Pi.  
   On PC, you can put the source codes wherever you want.

   **_!!! Important !!!_**  
   On Raspberry Pi, create a directory named **PointBlank** in the **home directory** and put the source codes inside like this:

        PointBlank
        ├─ PC/
        └─ rpi/

2. Upload the code `rpi/arduino_button/arduino_button.ino` to Arduino Uno.
3. Compile the source code in `rpi/motion_sensor/src` with command `make`.
4. Change `rpi/start.sh` to executable with `chmod +x`.
5. If you do not have I2C enabled on your Raspberry Pi, run `sudo raspi-config` and enable I2C under `Interfacing Options`.

### Hardware Installation
1. Connect the Analog five button keyboard module to Arduino Uno:

        Button      Arduino
        OUT ------- A0 (Analog In)
        VCC ------- 5V
        GND ------- GND

2. Connect Arduino Uno to Raspberry Pi with USB.
3. Affix MPU-9250 to the pointer firmly with the **y-axis** pointing forward.
4. Connect MPU-9250 to Raspberry Pi:

        MPU-9250    Raspberry Pi
        VCC ------- 3.3V
        GND ------- GND
        SCL ------- GPIO3 (pin 5)
        SDA ------- GPIO2 (pin 3)
        AD0 ------- GND

### Run PointBlank
1. On PC, run `python3 PC/settings.py` to customize PointBlank to your preference. Save and close after you are done.
2. On PC, run `sudo python3 PC/PointBlank.py` to start the main application.
3. On Raspberry Pi, run `sudo rpi/start.sh`.
4. Upon connection, you should see a message at the top-right corner of the screen.  
   **_Note:_** If you see messages on the terminal about something like "cannot connect due to pending actions" or "adapter changed by another process", it is most likely that the connection has failed. In this case, reopen the terminal window and repeat step 2.
   
5. Button usage:  
   ![button usage](https://drive.google.com/uc?id=1D0ilXYDdwIFlSyiLEO2fZ5tVq5Z5Dv9n)  
   **_Note:_** When pressing the activation button, please make sure that the pointer is oriented approximately towards the center of the screen to have the best experience.
 
6. After the presentation, press "Power Off" for 2 seconds and then release to shut down the pointer.

   **This will shut down Raspberry Pi.**

    You should see a message on screen indicating "PointBlank has disconnected". Wait until the green light on Raspberry Pi has stopped blinking, then flip the switch to cut power.

   To prevent Raspberry Pi from shutting down and only stop the program instead, comment out line 274 in `rpi/ble_server.py`.

**_Note:_** If you want Raspberry Pi to start the program automatically at startup, edit the file `/etc/rc.local` with root access.
   Add `sudo /home/pi/PointBlank/rpi/start.sh` before `exit 0`.

## Demo
[Youtube video](https://www.youtube.com/watch?v=mGobSX6rNwA&list=PLBc0A7aN8odutAUrcdlcwq_626UYvtjB_&index=1)
