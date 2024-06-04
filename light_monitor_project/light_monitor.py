import datetime
import sys
import os
import time
import yaml 
from zoneinfo import ZoneInfo
from argparse import ArgumentParser
import numpy as np
import serial
import serial.tools.list_ports
import pandas as pd

SERIAL_PORT_DATA_RATE = 9600

POSSIBLE_DEVICE_PATHS = [
    "/dev/ttyACM0", 
    "/dev/ttyACM1", 
    # Debugging on Yuval's mac mini - 
    "/dev/cu.usbmodem2401",
    "/dev/cu.usbmodem2301",
    # Debugging on a PC - 
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5" 
] 



CSV_FIELD_NAMES = ['sensorValue', 'dateTime']
FILE_WRITE_DELAY_HRS = 24
FILE_WRITE_DELAY_MINS = FILE_WRITE_DELAY_HRS * 60 # How many minutes we wait between each file dump
TIMEZONE_NAME = "Asia/Jerusalem"
print(f"minutes between each file dump: {FILE_WRITE_DELAY_MINS}")

def get_serial_device():
    """
    Get the device object for our serial port.

    TODO - Find a smarter way to find the device in case it has a different name 
    (e.g. - can be /dev/ttyACM0, /dev/ttyACM1 and so on)
    """   
    for path in POSSIBLE_DEVICE_PATHS:
        try:
            ser = serial.Serial(path, SERIAL_PORT_DATA_RATE, timeout=1)
            print(f"\tSuccessfully opened serial port {path}")
            return ser
        except serial.SerialException:
            pass

    raise Exception(f"No valid serial port could be found! Tried the following - {POSSIBLE_DEVICE_PATHS}")

def FindArduinoPort(SearchFor):
    """
    this function search for the port Arduino is connected to based upon a search word such as the device name

    ###ARGS###
    SearchFor - a string according to the function will search for the port.
    """     
    ports = list(serial.tools.list_ports.comports())
    # Iterate through each port and check if it's an Arduino board
    for port in ports:
        if SearchFor in port.description:
            print(f"Arduino board found on {port.device}")
            SerialPort=port.device
    return SerialPort  

def parse_arduino_data(arduino_raw_data):
    """
    this function accepts raw data from the serial port arduino is connected to and edit it such that we will get numbers, with no space between lines.

    ###ARGS###
    arduino_raw_data - a one line with semicolon as delimeter between values for example : 50;300;14.6
    """
    try:
        raw_data = str(arduino_raw_data,'utf-8')

        data_packet = raw_data
        data_packet = data_packet.strip('\r\n')
        data_packet = data_packet.split(";")
        data_packet = [float(x) for x in data_packet]
    except Exception as err:
        print(f"Failed parsing a row - {raw_data}. Error - {err}")
        return None
    return data_packet



def get_arduino_data(serial_device):
    """
    Read & parse sensor data from the arduino device (via the serial port).
    We return a dict with the parsed data from the sensors.
    """
    current_time = datetime.datetime.now()
    formatted_date = current_time.strftime("%Y_%m_%d")
    formatted_time = current_time.strftime("%H_%M_%S")

    try:
        arduino_raw_data = serial_device.readline()
    except Exception as err:
        print(f"Failed reading data from Arduino! {err}")
        return None

    data_packet = parse_arduino_data(arduino_raw_data)

    # Verify that the data was read properly. 
    # If our data dict has less than the expected CSV field name count (minus 1 for the datetime field
    # which we manually add), then there's been an error with reading the data 
    if (data_packet is None) or (len(data_packet) != (len(CSV_FIELD_NAMES) - 1)):
        print(f"Failed parsing data. Ignoring this record! (raw data was - {arduino_raw_data})")
        return None

    data_packet.insert(0, formatted_time)
    data_packet.insert(0, formatted_date)


    return data_packet
    

if __name__ == "__main__":
    print("Hello! This is the Arduino controller script!\n")

   
    ## Part 1 - Connect to the serial device
    try:
        serial_device = get_serial_device()
        print("\tSuccessfully connected to Serial device")
    except Exception as err:
        print(f"Failed connecting to the Serial device - `{err}`")
        sys.exit(1)
    
    

    ## Part 2 - This is the main part of the code, which runs in a loop and reads data from light
    ## sensor, and saves the daily light data to a csv file.
    
    data_from_last_day = [] # This array will handle the daily data, and will be reset once the day is over
    minute_counter = 1
    hour_loop_start_time = datetime.datetime.now()


    while True: 
        while serial_device.in_waiting == 0: 
            pass 
        
        # Read & aggregate data from the sensor
        current_time = datetime.datetime.now()
        print(f"Current UTC time is {current_time}\n")
        
        data_from_last_minute = [] # This array will handle data in each minute. It resets every minute. 

        minute_loop_start_time = datetime.datetime.now()

        # This loop should run for 1 minute.
        # Every second we get new data from the arduino, and store in an array.
        # in the end, it calculates the average light value for the last minute, and adds the current date and time.
        
        
        while True:
            data = get_arduino_data(serial_device) #returns data array ['date', 'time', 'sensorValue']
            if data is None: # There was an error, moving on and ignoring this specific read
                continue
            print(f"data: {data} \n")
            data_from_last_minute.append(data[2]) #append only light sensor value from current data array
            if (datetime.datetime.now() - minute_loop_start_time).seconds >= 59:
                one_minute_data = [data[0], data[1], np.round(np.mean(data_from_last_minute), 0)]
                print(f"\tFinished collecting data for {minute_counter} minutes, data for last minute is: {one_minute_data}")
                minute_counter = minute_counter + 1
                break
            time.sleep(1) #wait 1 seconds between each data aqcuisition from arduino. THIS DELAY HAS TO MATCH THE SAMPLING RATE OF THE ARDUINO!!!
        
        data_from_last_day.append(one_minute_data)
 
        minutes_since_start = (datetime.datetime.now() - hour_loop_start_time).total_seconds() / 60 #calculate time passed since start in minutes

        if minutes_since_start >= FILE_WRITE_DELAY_MINS: #if {FILE_WRITE_DELAY_HRS} hours passed since the start of data acquisition, export aggregated data to csv file.
            print(f"\t{FILE_WRITE_DELAY_HRS} hours have passed! Writing data to disk")
            
            # this part will create a directory for every month and save the daily data files in it, or save the daily data file in the current month directory if it already exists 
            
            curr_time = datetime.datetime.now().strftime("%H_%M")  #current time (H:M)         
            date_today = datetime.datetime.now().strftime("%Y_%m_%d") # current date
            base_path = r'/home/cohenlab/Desktop/light_monitor_project/Light_data'  
            #output_path = os.path.join(base_path, date_today)        
            filename = os.path.join(base_path, rf'{date_today}.csv')        

            #os.makedirs(output_path, exist_ok = True)

            #filename = os.path.join(output_path, rf'{curr_time}.csv')

            hourly_data_df = pd.DataFrame(data_from_last_day)
            hourly_data_df.columns = ['date', 'Time', 'sensorValue']
            hourly_data_df.to_csv(filename, index=False)

            print(f"\tSuccessfully wrote  data to {base_path}")
            
            # Reset the loop start time, the daily data array, the minutes counter and then continue the loop.
            hour_loop_start_time = datetime.datetime.now()
            data_from_last_day = [] 
            minute_counter = 1

   
