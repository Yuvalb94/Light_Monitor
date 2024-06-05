# Light Monitor set-up
This guide will let you through the neccessary steps to set up a working light monitor.
1. Setting up the Raspberry pi and all it's pre-requisites.
2. Building the light sensor box.
3. Setting up and connecting the Arduino

## 1. Setting up the Raspberry Pi 
In order to set up the Raspberry pi 4 computer correctly follow these steps:
1. 


### Install the Raspberry Pi Operating system 
  Use [Raspberry Pi imager](https://www.raspberrypi.com/software/) to install the Rasraspberry pi OS (Legacy, 32 bit) operating system onto a compatible SD card.
  Set the user name to cohenlab and the password to the current lab user password.
  Now you can assemble the Raspberry Pi:  - insert the SD card in it's place, connect a keyboard, screen, mouse, ethernet, and power.

### Adding the Raspberry Pi to the Wis systems
to connect to the Wis network and use storWis, we need to extract its MAC address and contact [Arthur Kalntarov](artur.kalantarov@weizmann.ac.il) to do that .
In terminal type:
```
ifconfig
```
Locate the MAC address in the first part of the text that opens (eth0). It is written after the word "ether" and has 6 pairs of characters separated by a colon(:).
Send it to Arthur and ask him to add it.
Once the Raspberry pi has been added, you will see on the top right corner of the screen next to the clock - two blue arrows up and down, and it will display "eth0: configured".

### Synchronizing the Raspberry Pi clock
  The Raspberry Pi clock uses the network to synchronize its clock. This is done by connecting to a server. The default server does not work properly. 
  So in this step, we will change the default server source. 
  Without a synchronized clock, we won't be able to install important updates and libraries which are essential.
  
Set the raspberry source as follows:
1. in the Raspberry Pi terminal type 
```
sudo nano /etc/apt/sources.list
```
2.  uncomment the bottom line 
3. In the file: change the mirror URL to a desired one (a list  of URLs is attached [here] (https://www.raspbian.org/RaspbianMirrors))
a mirror link has several components. Change only the existing  mirror URL (not the distribution or components)! 
```
deb http://<mirror-url>/ <distribution> <components>
```
for example:
```
deb http://raspbian.mirror.garr.it/mirrors/raspbian/raspbian/ bullseye main contrib non-free rpi

```
- mirror-URL: The URL of the mirror you want to use.
- distribution: The name of the distribution (e.g., stretch, buster, etc.).
- components: The software components you want to include (e.g., main, contrib, non-free, etc.).

4. Save and exit

### Installing updates 
Note that the last command in the code block below is the installation of the samba client which will allow us to connect to storWIS, and not a general update.
  Now run the following commands in the terminal.
  ```
  sudo apt-get update
  sudo apt-get upgrade 
  sudo apt-get install samba-common smbclient samba-common-bin smbclient  cifs-utils

  ```

### Upload the repository and install required libraries

* Download the [light_monitor](https://github.com/NeuralSyntaxLab/acoustic_chamber_environment_control/tree/main)  repository as by clicking on `Code > Download zip.` extract the zip file onto the dashboard.
  now you should have a folder by the same name containing all the repository content.

* Install neccesary Python dependencies on the Raspberry pi:
  ```
  pip install pandas

  sudo apt install libopenblas-dev

  ```
* Install Arduino IDE: In terminal type `sudo apt-get install arduino`. This could take a few minutes.

* Connect an Arduino microcontroller to the Raspberry Pi and open the [arduino_code_L.ino](https://github.com/Yuvalb94/NeuralSyntaxLab_Yuval_LightMonitor/blob/main/arduino_code_L/arduino_code_L.ino) file using the Arduino IDE. 
* load arduino_code.ino code onto the Arduino using the IDE. (see instructions [here](https://docs.arduino.cc/learn/starting-guide/the-arduino-software-ide).

