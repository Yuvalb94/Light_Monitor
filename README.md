# Light Monitor set-up
This guide will let you through the neccessary steps to set up a working light monitor.
1. Building the light sensor box.
2. Setting up the Raspberry pi and all it's pre-requisites.
3. Setting up and connecting the Arduino
## 1. Building the light sensor box

CONTENT TO BE ADDED

## 2. Setting up the Raspberry Pi 
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

  
### mounting storWis onto Raspberry Pi.
storWis is used to back up all the files whic
In terminal typeh contain the environment monitoring data.
we can also access storWis relatively easily from different computers such that we have access to the data from any computer that is connected to the institute network.
 Create a credentials file, for instance, at the /home directory.
 Here, we will call it cred
The credential file is a text file containing the following in the following format:
```
username=USERNAME(the desired username) 
password=PASWORD(its password) 
domain=wismain
```
Type in terminal:
```
sudo nano /etc/fstab
```
At the bottom of the file add the following line:
```
//isi.storwis.weizmann.ac.il/labs/cohen /mnt/STORWIS cifs noauto,users,credentials=/PATH/to/cred,dir_mode=0777,file_mode=0777,noserverino,x-systemd.automount 0 0
```
Change the path to the credentials file, and the path to mounting point if you like (instead of /mnt/STORWIS. 

Save and exit

In terminal type
```
sudo mount -a
```
Now you should have Storwis folders in your directory, in the above example at /mnt.

IMPORTANT: Storwis should be mounted only when the light monitor is connected to the internet!
If you are placing the light sensor in a romm without internet connection, make sure to unmount storwis from the Raspberry pi:
```
sudo umount /mnt/path/to/mount/point (/mnt/STORWIS)
```

## How to automatically run the script when Raspberry Pi is turned on
The script 'light_monitor.py' is out main script and it should be launched automatically when Raspberry Pi is turned on.

This is done using the following tools - 
1. We have a bash script, called `startup_script.sh` which is an infinite loop that keep relaunching the script and waits for it to finish. If it crashes, it's supposed to run again.
2. When Raspberry Pi turns on, we automatically run the `startup_script.sh` script.

To automatically run the script when the machine turns on - 

*remember to change the '/path/to/startup_script.sh' part with the actual path to the startup script*
1. Modify the bash script permission. in Terminal type : `chmod +x path/to/start_Script.sh`
2. In terminal Type `sudo nano /etc/xdg/lxsession/LXDE-pi/autostart`
3. Add the following command to the end of the file - 
`@lxterminal -e /path/to/startup_script.sh`
  save and exit terminal.
4. create a folder called light_data that will store the data written by the main script.
5. In the script light_monitor.py, make sure that the base path is the path to the folder you created in the previous step.
6. Reboot the machine to verify that it's working









   
