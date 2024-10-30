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
from matplotlib.ticker import FuncFormatter
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

def accumulate_data(path_to_light_data, write = False, filename='joined_data.csv'):
        # make a list that contains filenames of all csv files in folder, sorted by date
        light_data_files = sorted(glob.glob(path_to_light_data + '/*.csv')) 
        #read first file to dataframe
        light_data = pd.read_csv(light_data_files[0]) #, index_col=0)
        #iterate through all the other csv files and concatenate them veritcally
        for file in light_data_files[1:]:
            temp = pd.read_csv(file) #, index_col=0)
            light_data = pd.concat([light_data, temp], ignore_index=True)

        if write == True:
            filename = os.path.join(path_to_light_data, filename)
            light_data.to_csv(filename, index=True)

        return light_data

def plot_data(data, xaxisby='hours from start', date_fmt = '%Y-%m-%d %H:%M:%S.%f', title='light intensity', show=False):
    fig, ax = plt.subplots()

    # Extract the dates and times separately from the time column
    times = [datetime.datetime.strptime(time, f"{date_fmt}").strftime("%H:%M") for time in data["Time"]]
    dates = [datetime.datetime.strptime(time, f"{date_fmt}").strftime("%Y-%m-%d") for time in data["Time"]]
    # times = [time.strftime("%H:%M") for time in data["Time"]]
    # dates = [time.strftime("%Y-%m-%d") for time in data["Time"]]

    # Calculate the ticks of the date shifts
    unique_dates = np.unique(dates)
    date_shift_ticks  = []
    for date in unique_dates:
        date_shift_ticks.append(dates.index(date))

    # Plot the weight data
    ax.plot(data.index, data[birdname], marker='.', linestyle='-')

    # Edit time axis
    if xaxisby == 'datetime': 
        ax.set_xticks(data.index[::3600], labels=times[::3600])
        ax.set_xlabel("time(H_M)")
        
        # Plot vertical lines in positions of date shifts
        for date in date_shift_ticks:
            ax.axvline(x=date, color='red', linestyle='--')
    
            # Add the value of the index next to the vertical line
            ax.text(date, np.mean(ax.get_ylim()), str(dates[date]), color='red', rotation=90, va='center', ha='right')

    else: # Plot x-axis as hours from start
        ax.set_xticks(data.index[::3600], labels=np.arange(0, len(data.index[::3600])))
        ax.set_xlabel("hours from start")

    plt.xticks(rotation=90)                  
    ax.set_ylabel("weight(g)")
    plt.title(f"{title}")
    ax.legend()
    if show == True:
        plt.show()
    else:
        return fig, ax
    

def time_to_seconds(t):
    total_seconds = t.hour * 3600 + t.minute * 60 + t.second
    return total_seconds

# Function to format y-axis ticks as HH:MM
def format_func(value, tick_number):
    hours = int(value // 3600)
    minutes = int((value % 3600) // 60)
    return f"{hours:02}:{minutes:02}"

if __name__ == "__main__":
    print("hello")
    timeString_HMS = "%H_%M_%S" # the format of the time (string) that we want to convert to datetime object
    timeString_YMD = "%Y_%m_%d" # the format of the date (string) that we want to convert to datetime object
    location_info = get_weizmann_location_object()
    location_info2 = astral.LocationInfo('Anti-Weizmann', 'Anti-Israel', TIMEZONE_NAME, ANTI_WEIZMANN_LAT, WEIZMANN_LONG)
    days_shift = 0
    #read and join all light sensor data
    path_to_light_data = r'/Users/cohenlab/Desktop/light_monitor_project/light_data/room141'
    # light_data = pd.read_csv(fr"{path_to_light_data}/03_01_24.csv", index_col=0)
    light_data = accumulate_data(path_to_light_data, write=False)
    light_data['sensorValue'][light_data['sensorValue'] == 1] = 0
    # get daylight hours from our data
    light_status = pd.DataFrame(columns = ['date', 'light_on', 'light_off'])
    unique_dates = light_status['date'] = np.unique(light_data['date']) #dates of light sensor reading data in string. for later use.
    # print(light_data[230:250])

    
    light_status['light_on'][0] = np.nan #in this case first day has no recording from before 8am so no light on hour. initiate with NaN

    prev = light_data.sensorValue[0] # initiate prev as the value of the first sensorValue read
    #iterate through all sensorValue reads and compare them to the value of the previous reading.
    #   - if the current reading is bigger than the previous one, and the previous value was 0, this is the time the light turned on.
    #   - if the current reading is smaller than the previous one, and it is 0, this is the time the light switched off.
    #   switch on / off times for each day will be stashed in the according column in light_status Dataframe.
    for i,val in enumerate(light_data.sensorValue):
        if prev < val and prev == 0:
            light_status['light_on'][light_status['date']==light_data['date'][i]] = light_data['Time'][i]
        if prev > val and val == 0:
            light_status['light_off'][light_status['date']==light_data['date'][i]] = light_data['Time'][i]
        prev = val

    light_status['light_on'][0] = light_status['light_on'][1]
    light_status['light_off'][26] = light_status['light_off'][25]
    
    print(light_status[82:])
    # plt.plot(light_data['Time'], light_data['sensorValue'])
    # plt.show()
    df = pd.DataFrame(light_status)

    df['date'] = pd.to_datetime(df['date'], format=timeString_YMD)
    df['light_on'] = df['light_on'].str.replace('_', ':')
    df['light_off'] = df['light_off'].str.replace('_', ':')

    df['light_on'] = pd.to_datetime(df['light_on'], format='%H:%M:%S').dt.time
    df['light_off'] = pd.to_datetime(df['light_off'], format='%H:%M:%S').dt.time
    
    total_seconds = df['light_on'][0].hour*3600 + df['light_on'][0].minute*60 + df['light_on'][0].second
    print(total_seconds)


    df['light_on_seconds'] = df['light_on'].apply(time_to_seconds)
    df['light_off_seconds'] = df['light_off'].apply(time_to_seconds)

    # Convert light on/off times to fractional hours (e.g., 1.5 for 1 hour 30 minutes)
    df['light_on_hours'] = df['light_on_seconds'] / 3600
    df['light_off_hours'] = df['light_off_seconds'] / 3600

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df['date'], df['light_on_hours'], 'o', label='Light On Times', color='green')
    ax.plot(df['date'], df['light_off_hours'], 'o', label='Light Off Times', color='black')

    # Format the x-axis
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y_%m_%d'))
    plt.xticks(rotation=45)

    # # Format the y-axis to show times
    # ax.yaxis_date()
    # ax.yaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    # ax.yaxis.set_major_locator(mdates.HourLocator(interval=1))
    # ax.yaxis.set_major_formatter(FuncFormatter(format_func))

    plt.xlabel('Date')
    plt.ylabel('Time')
    plt.title('Light On and Off Times')
    plt.legend()
    plt.grid(True)

    plt.show()
    # Extract the dates and times separately from the time column
    # times = [datetime.datetime.strptime(time, f"{date_fmt}").strftime("%H:%M") for time in data["Time"]]
    # dates = [datetime.datetime.strptime(date, f"{timeString_MD}").strftime("%Y_%m_%d") for date in light_status["date"]]
    # light_on_times = [datetime.datetime.strptime(time, f"{timeString_HMS}").strftime("%H:%M:%S") for time in light_status['light_on'][1:]]
    # light_on_times.insert(0, 0)
    # light_off_times = [datetime.datetime.strptime(time, f"{timeString_HMS}").strftime("%H:%M:%S") for time in light_status['light_off'][0:-1]]
    # light_off_times.append(0)
    # print(type(light_off_times[2]))
    # times = [time.strftime("%H:%M") for time in data["Time"]]
    # dates = [time.strftime("%Y-%m-%d") for time in data["Time"]]

    # # Calculate the ticks of the date shifts
    # unique_dates = np.unique(dates)
    # date_shift_ticks  = []
    # for date in unique_dates:
    #     date_shift_ticks.append(dates.index(date))

    # times = [datetime.datetime(2023, 1, 1, 8) + datetime.timedelta(hours=i) for i in range(10)]

    # Plot the weight data
    # ax.plot(data.index, data[birdname], marker='.', linestyle='-')
    # ax.plot(dates, light_on_times, color='yellow', label='light on times')
    # ax.plot(dates, light_off_times, color='black', label='light off times')


    # # Edit time axis
    # if xaxisby == 'datetime': 
    #     ax.set_xticks(data.index[::3600], labels=times[::3600])
    #     ax.set_xlabel("time(H_M)")
        
    #     # Plot vertical lines in positions of date shifts
    #     for date in date_shift_ticks:
    #         ax.axvline(x=date, color='red', linestyle='--')
    
    #         # Add the value of the index next to the vertical line
    #         ax.text(date, np.mean(ax.get_ylim()), str(dates[date]), color='red', rotation=90, va='center', ha='right')

    # else: # Plot x-axis as hours from start
    #     ax.set_xticks(data.index[::3600], labels=np.arange(0, len(data.index[::3600])))
    #     ax.set_xlabel("hours from start")

    # #  Set the limits for the y-axis
    # start_time = datetime(2023, 1, 1, 8)  # 08:00 AM
    # end_time = datetime(2023, 1, 1, 18)   # 06:00 PM
    # ax.set_ylim(start_time, end_time)

    # plt.xticks(rotation=90)                  
    # ax.set_ylabel("date")
    # # plt.title(f"{title}")
    # ax.legend()
    # plt.show()
  
    # light_status['date'] = pd.to_datetime(light_status['date'], format="%Y_%m_%d")
    # light_status['light_on'] = pd.to_datetime(light_status['light_on'], format="%H_%M_%S")
    # light_status['light_off'] = pd.to_datetime(light_status['light_off'], format="%H_%M_%S")
    # # light_status['light_on'][7] += datetime.timedelta(minutes=55) # fix mistake in a specific day
    # #create an array of sunrise-to-sunset time deltas for each day from the light sensor data:
    # #First, convert light on and light off times to decimal hours so that they could be substracted. Then, find the delta between them in decimal hours.
    # light_on_times = [time_to_decimal_hours(time) for time in light_status['light_on'].tolist()]
    # light_off_times = [time_to_decimal_hours(time) for time in light_status['light_off'].tolist()]
    # light_delta = (np.array(light_off_times) - np.array(light_on_times))
    # print("light delta:", light_delta)

    # # create a datetime vector of dates we wish to compare out data to - this array will begin in start_date and end in end_date.
    # start_date = pd.to_datetime(light_status['date'], format="%H_%M_%S")[0] + datetime.timedelta(days=days_shift)
    # end_date = light_status.date.iloc[-1] + datetime.timedelta(days=days_shift)
    # dates = generate_dates(start_date, end_date) #generate the dates array
    # dates_in_format = [date.strftime('%Y_%m_%d') for date in dates]

    # #calculate the indices of days without data for later use
    # orig_days = dates_in_format
    # data_days = light_status_dates
    # missing_dates = []
    # missing_dates_indices = []
    # #def find_missing_dates(orig_dates, data_dates):
    # for i, date in enumerate(orig_days[0:(len(orig_days)-days_shift)]):
    #     if date in data_days:
    #         continue
    #     else:
    #         missing_dates.append(date)
    #         missing_dates_indices.append(i)
    

    # # calculate sunrise([0]) and sunset([1]) times for location_info for every day in dates
    # sunrise_times = [get_sun_times_by_day(location_info, date)[0] for date in dates]
    # sunset_times = [get_sun_times_by_day(location_info, date)[1] for date in dates]

    # #transform datetime object to scalable decimal hour(float object) before plotting
    # sunrise_times = [time_to_decimal_hours(time) for time in sunrise_times] 
    # sunset_times = [time_to_decimal_hours(time) for time in sunset_times]

    # #calculate the delta between sunrise and senset in the defined location for each day (float object)
    # sun_delta = (np.array(sunset_times) - np.array(sunrise_times)).tolist()
    
    # light_status_dates_list = [(date - datetime.timedelta(days=4)) for date in light_status['date'].tolist()]

    # #plotting the data
    # plt.figure()
    # plt.plot(dates, sun_delta, marker='.', linestyle='-', color='b', label='Sun_delta')
    # plt.plot(light_status_dates_list, light_delta, marker='.', linestyle='-', color='g', label='Light_delta')
    # plt.xticks(rotation=45)
    # plt.tight_layout()
    # plt.yticks(ticks=np.linspace(9.5, 15, 21)) # set y axis perimeter to focus on the current delta values

    # j=0
    # #add text with value next to each mark from sun_delta and light_delta.
    # for i in range(len(sun_delta)):
    #     # add text marks for sun_delta values
    #     # plt.text(dates[i], sun_delta[i]+0.2, str(np.round(sun_delta[i], 2)), va='top', ha='center', c='b')
    #     if i in missing_dates_indices:
    #         j+=1
    #     # else:
    #         #add text values for light_delta values
    #         # plt.text(dates[i], light_delta[i-j]-0.2, str(np.round(light_delta[i-j], 2)), va='bottom', ha='center', c='g')
    #         #add dates for which the time delta is calculated
    #         # plt.text(dates[i], 9.9, str(light_status_dates[i-j]), va='top', ha='center', c='g', rotation=45, fontsize='small')
    # # for i in range(len(light_delta)):
    # #     plt.text(dates[i], light_delta[i]-0.2, str(np.round(light_delta[i], 2)), va='bottom', ha='center', c='g')
    # #     plt.text(dates[i], 9.9, str(light_status_dates[i]), va='top', ha='center', c='g', rotation=45, fontsize='small')

    # # plt.text(dates[8], 10.1, "Bird Room dates:", c='g', va='top', ha='right', fontsize = 'medium')
    # plt.text(dates[1], 14.9, f"{days_shift} days shift", c='k', va='top', ha='right', fontsize = 'large')

    # plt.legend()
    # plt.xlabel('Weizmann dates')
    # plt.ylabel('Time Delta (hours)')
    # plt.title('Time deltas between sunrise and sunset in Anti-Weizmann vs. light on and light off in Birds room')
    # plt.show()
   