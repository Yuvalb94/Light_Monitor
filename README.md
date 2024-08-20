# Light Monitor set-up
The Light Monitor is a system designed to record and track changes in lighting within a room, or an experimantal environment (such as an acoustic chamber for housing birds).

The setup contains a light-dependant-resistor (LDR), an Arduino microcontroller and a Raspberry Pi minicomputer. The minicomputer runs a [continuous script](https://github.com/Yuvalb94/NeuralSyntaxLab_Yuval_LightMonitor/blob/d589808785becd07bf68272145cf4240f085d43c/light_monitor.py) communicated with the Arduino. The Arduino is connected to the LDR, which sends the light reading every second. The data is stored in a .csv file on the minicomputer for further analysis. 

The [startup script](https://github.com/Yuvalb94/NeuralSyntaxLab_Yuval_LightMonitor/blob/d589808785becd07bf68272145cf4240f085d43c/startup_script.sh) is a shell script designed to command the minicomputer to run the main control script at startup, making it easy to use the system without the need to operate it as it runs.



