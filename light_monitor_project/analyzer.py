import datetime
import os
import time 
import sys
import os
import time
from zoneinfo import ZoneInfo
import astral
from astral.sun import sun
import pandas as pd
from matplotlib import pyplot as plt, dates as mdates
import numpy as np
import glob 
TIMEZONE_NAME = "Asia/Jerusalem"
WEIZMANN_LAT = 31.905111
ANTI_WEIZMANN_LAT = -31.905111
WEIZMANN_LONG = 34.808349

def get_astral_default_location_object():
    """
    Returns a default LocationInfo object for Israel, which is "Jerusalem".
    """
    db = astral.geocoder.database()
    location_object = astral.geocoder.lookup("Jerusalem", db)
    return location_object

def get_weizmann_location_object():
    """
    Return the LocationInfo object for the Weizmann Institute, which is determined by coordinates.
    """
    location_object = astral.LocationInfo('Rehovot', 'Israel', TIMEZONE_NAME, WEIZMANN_LAT, WEIZMANN_LONG)
    return location_object


def get_sun_times_by_offset(city: astral.LocationInfo, days_offset: int = 0,Hours_offset: int =0):
    """
    Receive a city (LocationInfo object) and return the sunrise & sunset times, for the current date.

    In addition, we receive a `days_offset` value (default = 0), which indicates whether we want a delay
    in our date calculation
    """

    date = datetime.date.today() + datetime.timedelta(days=days_offset) 

    sun_info = sun(city.observer, date=date, tzinfo=ZoneInfo(TIMEZONE_NAME))
    sunrise_time = sun_info["sunrise"]
    sunset_time = sun_info["sunset"]

    return (sunrise_time, sunset_time)

def get_sun_times_by_day(city: astral.LocationInfo, date: datetime.datetime.now()):
    """
    Receive a city (LocationInfo object) and return the sunrise & sunset times, for a desierd date.
    it's default is today's date
    """

    sun_info = sun(city.observer, date=date, tzinfo=ZoneInfo(TIMEZONE_NAME))
    sunrise_time = sun_info["sunrise"]
    sunset_time = sun_info["sunset"]

    return (sunrise_time, sunset_time)

def generate_dates(start_date, end_date):
    delta = datetime.timedelta(days=1)
    current_date = start_date
    dates = []

    while current_date <= end_date:
        dates.append(current_date)
        current_date += delta

    return dates

def time_to_decimal_hours(time):
    return time.hour + time.minute / 60 + time.second / 3600

def accumulate_data(path_to_light_data, write = False, filename='joined_data'):
        # make a list that contains filenames of all csv files in folder, sorted by date
        light_data_files = sorted(glob.glob(path_to_light_data + '/*.csv')) 
        #read first file to dataframe
        light_data = pd.read_csv(light_data_files[0], index_col=0)
        #iterate through all the other csv files and concatenate them veritcally
        for file in light_data_files[1:-1]:
            temp = pd.read_csv(file, index_col=0)
            light_data = pd.concat([light_data, temp], ignore_index=True)

        if write == True:
            filename = os.path.join(path_to_light_data, filename)
            light_data.to_csv(filename, index=True)

        return light_data


if __name__ == "__main__":
    print("hello")
    timeString_HMS = "%H:%M:%S"
    timeString_MD = "%m-%d"
    location_info = get_weizmann_location_object()
    location_info2 = astral.LocationInfo('Anti-Weizmann', 'Anti-Israel', TIMEZONE_NAME, ANTI_WEIZMANN_LAT, WEIZMANN_LONG)

    #read and join all light sensor data
    path_to_light_data = r'/Users/cohenlab/Desktop/light_monitor_project/light_data/test1'
    # light_data = pd.read_csv(fr"{path_to_light_data}/03_01_24.csv", index_col=0)
    light_data = accumulate_data(path_to_light_data, write=False)
    # get daylight hours from our data
    # temp = pd.read_csv(r'/Users/cohenlab/Desktop/light_monitor_project/light_data/test1')
    light_status = pd.DataFrame(columns = ['date', 'light_on', 'light_off', 'delta'])
    Light_status_dates = light_status['date'] = np.unique(light_data['date'])

    light_status['light_on'][0] = np.nan #in this case first day has no recording from before 8am so no light on hour. initiate with NaN
    prev = light_data.sensorValue[0]
    for i,val in enumerate(light_data.sensorValue):
        if prev < val and prev == 0:
            light_status['light_on'][light_status['date']==light_data['date'][i]] = light_data['Time'][i]
        if prev > val and val == 0:
            light_status['light_off'][light_status['date']==light_data['date'][i]] = light_data['Time'][i]
        prev = val
    print("light_status:", light_status)
    print(np.unique(light_data['sensorValue']))
    light_status['date'] = pd.to_datetime(light_status['date'], format="%Y_%m_%d")
    light_status['light_on'] = pd.to_datetime(light_status['light_on'], format="%H_%M_%S")
    light_status['light_off'] = pd.to_datetime(light_status['light_off'], format="%H_%M_%S")
    light_on_times = [time_to_decimal_hours(time) for time in light_status['light_on'].tolist()]
    light_off_times = [time_to_decimal_hours(time) for time in light_status['light_off'].tolist()]
    light_delta = (np.array(light_off_times) - np.array(light_on_times))
    
    start_date = pd.to_datetime(light_status['date'], format="H_%M_%S")[0] + datetime.timedelta(days=7)
    end_date = light_status.date.iloc[-1] + datetime.timedelta(days=7)
    dates = generate_dates(start_date, end_date)
    sunrise_times = [get_sun_times_by_day(location_info2, date)[0] for date in dates]
    sunset_times = [get_sun_times_by_day(location_info2, date)[1] for date in dates]
    sunrise_times = [time_to_decimal_hours(time) for time in sunrise_times]
    sunset_times = [time_to_decimal_hours(time) for time in sunset_times]
    sun_delta = (np.array(sunset_times) - np.array(sunrise_times)).tolist()
    
    plt.figure()
    plt.plot(dates, sun_delta, marker='.', linestyle='-', color='b', label='Sun_delta')
    plt.plot(dates, light_delta, marker='.', linestyle='-', color='g', label='Light_delta')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.yticks(ticks=np.linspace(13, 15, 21))
    for i in range(len(sun_delta)):
        plt.text(dates[i], sun_delta[i]+0.1, str(np.round(sun_delta[i], 2)), va='top', ha='center', c='b')
        plt.text(dates[i], light_delta[i]-0.1, str(np.round(light_delta[i], 2)), va='bottom', ha='center', c='g')
        plt.text(dates[i], 13.2, str(Light_status_dates[i]), va='top', ha='center', c='g', rotation=45, fontsize='small')
    plt.text(dates[4], 13.4, "Bird Room dates:", c='g', va='top', ha='right', fontsize = 'medium')
    plt.text(dates[4], 14.9, "7 days forward shift", c='k', va='top', ha='right', fontsize = 'large')

    plt.xlabel('Anti-Weizmann dates')
    plt.ylabel('Time Delta (hours)')
    plt.title('Time deltas between sunrise and sunset in Anti-Weizmann vs. light on and light off in Birds room')
    plt.show()
   