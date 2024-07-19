import board
import RPi.GPIO as GPIO
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import os
import json
import threading
import time
from datetime import datetime
import random
import schedule

import csv
import glob
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c

# Thresholds
buck_current_threshold = 2.25 
absorption_voltage_threshold = 14.4 
float_voltage_threshold = 13.6 
absorption_current_treshold = 0.05

# Mode
mode = "BUCK" # initial mode

# Define your voltage and current limits
voltage_limit = absorption_voltage_threshold  # Example voltage limit
current_limit = buck_current_threshold   # Example current limit



now = datetime.now()
five_minutes_start = (now.hour * 60 + now.minute)- 360 // 10
date_start = now.day

toggled = False
json_data = {}

# Konfigurasi pin PWM
pin_pwm1 = 18
pin_pwm2 = 19

# Mengatur mode pin dan inisialisasi pin PWM
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_pwm1, GPIO.OUT)
GPIO.setup(pin_pwm2, GPIO.OUT)

# Frekuensi PWM yang dapat diubah sesuai kebutuhan
frekuensi_pwm = 5000

# Inisialisasi objek PWM
pwm1 = GPIO.PWM(pin_pwm1, frekuensi_pwm)
pwm2 = GPIO.PWM(pin_pwm2, frekuensi_pwm)

# Inisialisasi I2C dan objek ADS1115 untuk pembacaa
# Inisialisasi display OLED
oled_reset = digitalio.DigitalInOut(board.D4)
WIDTH, HEIGHT, BORDER = 128, 64, 5
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)
oled.fill(0)
oled.show()
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('PixelOperator.ttf', 16)

# Variabel untuk menyimpan nilai sebelumnya
nilaipwm1, nilaipwm2 = 100, 5
dayaSebelumnya, teganganSebelumnya = 0, 0

# Define the maximum size of the buffer
max_size = 100  # Adjust this number to your desired buffer size

arus1 = 0
arus2 =  0
tegangan1 = 0
tegangan2 = 0
presentase = 0

def get_five_minutes_since_6am():
    now = datetime.now()
    current_time = now.time()
    
    # Ensure the current time is between 6 AM and 6 PM
    if 6 <= current_time.hour < 18:
        total_minutes = (current_time.hour - 6) * 60 + current_time.minute
        five_minutes_intervals = total_minutes // 5
        return five_minutes_intervals
    else:
        raise ValueError("Current time is not between 6 AM and 6 PM")


# Function to create a new circular buffer
def create_circular_buffer(size):
    return [0] * size, 0  # Buffer list and current index

# Function to add a new value to the buffer
def add_to_buffer(buffer, index, value, max_size):
    buffer[index] = value
    index = (index + 1) % max_size  # Increment and wrap the index
    return index

# Initialize the circular buffers for I and V
I_buffer, I_index = create_circular_buffer(max_size)
V_buffer, V_index = create_circular_buffer(max_size)

# Define a threshold for change
threshold_I = 0.1  # Adjust this value as needed for current
threshold_V = 1   # Adjust this value as needed for voltage

# Function to check if the new value is significantly different from all existing values
def is_significantly_different(new_value, existing_values, threshold):
    return all(abs(new_value - value) >= threshold for value in existing_values)
def calculate_battery_percentage(voltage):
    full_charge_voltage = 12.73  # Voltage of a fully charged battery
    discharge_voltage = 11.36    # Voltage of a fully discharged battery

    if voltage > full_charge_voltage:
        return 100  # Battery is fully charged or above
    elif voltage < discharge_voltage:
        return 0  # Battery is fully discharged or below
    else:
        # Calculate the percentage of the battery's charge
        percentage = ((voltage - discharge_voltage) / (full_charge_voltage - discharge_voltage)) * 100
        return round(percentage)  # Round to the nearest whole number
def log_readings():
    
    now = datetime.now()
    current_time = now.time()
    # if current_time >= datetime.time(6, 0) and current_time <= datetime.time(18, 0):
    five_minutes = get_five_minutes_since_6am()
    # Read the JSON file
    with open('pipe.json', 'r') as file:
        data = json.load(file)
    if(now.day%2):
        five_minutes += 144
    print("five_minutes",five_minutes)

     # Define CSV file name
    csv_filename = 'log.csv'

    # Check if CSV file exists, if not, create it and write the header
    if not os.path.isfile(csv_filename):
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'Battery Current', 'Panel Current', 'Battery Voltage', 'Panel Voltage', 'Charging Stage','Temperature'])

    # Write the data to the CSV file
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([int(time.time()),round(arus2, 2),round(arus1, 2),round(tegangan2, 2),round(tegangan1, 2),mode])


    with open('pipe.json', 'r') as file:
        data = json.load(file)
    
    data['readings']['batteryCurrent'] = round(arus2, 2)
    data['readings']['panelCurrent'] = round(arus1, 2)
    data['readings']['batteryVoltage'] = round(tegangan2, 2)
    data['readings']['panelVoltage'] = round(tegangan1, 2)
    data['readings']['temp'] = round(read_temp(), 2)
    data['readings']['soc'] = round(presentase, 2)

    data['stats']['daily']['soc'][five_minutes] = round(presentase, 2)

    data['stats']['daily']['temp'][five_minutes] = round(read_temp(), 2)    
    data['stats']['curveIV']['voltage'] = V_buffer
    data['stats']['curveIV']['current'] = I_buffer

    data['details']['lastUpdate'] = int(time.time())

    data['details']['status'] = mode

    data['settings']['toggleUpdate'] = False
    print("curve,",data['stats']['curveIV'])
    
    # Write the modified data back to the file
    with open('pipe.json', 'w') as file:
        json.dump(data, file, indent=4)    
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.text((0, 0), "Syncing...", font=font, fill=255)
    
def log_daily_stats():
     # Define CSV file name
    csv_filename = 'log.csv'

    # Check if CSV file exists, if not, create it and write the header
    if not os.path.isfile(csv_filename):
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time', 'Battery Current', 'Panel Current', 'Battery Voltage', 'Panel Voltage', 'Charging Stage','Temperature'])

    # Write the data to the CSV file
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([int(time.time()),round(arus2, 2),round(arus1, 2),round(tegangan2, 2),round(tegangan1, 2),mode,read_temp()])

    now = datetime.now()
    current_time = now.time()
    # if current_time >= datetime.time(6, 0) and current_time <= datetime.time(18, 0):
    five_minutes = get_five_minutes_since_6am()

    # Read the JSON file
    with open('pipe.json', 'r') as file:
        data = json.load(file)
    if(now.day%2):
        five_minutes += 144
    print("five_minutes",five_minutes)
    # Modify the data
    # For example, add a new key-value pair
    # print("daily,",current_time,five_minutes,five_minutes_start,now.day)
    data['readings']['batteryCurrent'] = round(arus2, 2)
    data['readings']['panelCurrent'] =round(arus1, 2)
    data['readings']['batteryVoltage'] = round(tegangan2, 2)
    data['readings']['panelVoltage'] = round(tegangan1, 2)     # Write the modified data back to the file
    data['readings']['temp'] = round(read_temp(), 2)
    data['readings']['soc'] = round(presentase, 2)

    data['stats']['daily']['soc'][five_minutes] = round(presentase, 2)

    data['stats']['daily']['temp'][five_minutes] = round(read_temp(), 2)
    data['stats']['daily']['batteryCurrent'][five_minutes] = round(arus2, 2)
    data['stats']['daily']['panelCurrent'][five_minutes] = round(arus1, 2)
    data['stats']['daily']['batteryVoltage'][five_minutes] = round(tegangan2, 2)
    data['stats']['daily']['panelVoltage'][five_minutes] = round(tegangan1, 2)    # Write the modified data back to the file
    
    data['settings']['toggleUpdate'] = False    # Write the modified data back to the file
    data['details']['lastUpdate'] = int(time.time())
    data['details']['status'] = mode
    
    with open('pipe.json', 'w') as file:
        json.dump(data, file, indent=4)
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.text((0, 0), "Logging...", font=font, fill=255)
        
def multiply_and_sum(arr1, arr2):
    return sum(a * b for a, b in zip(arr1, arr2))

def split_and_return(arr, return_upper=False):
    mid = len(arr) // 2  # Find the mid index
    lower = arr[:mid]    # Everything up to the mid
    upper = arr[mid:]    # Everything from the mid onwards
    return upper if return_upper else lower
    
def log_monthly_stats():
    now = datetime.now()
    date = now.day
    evenDay = False
    with open('pipe.json', 'r') as file:
        data = json.load(file)
    if(now.day%2):
        date += 31
        evenDay = True
    data['details']['lastUpdate'] = int(time.time())
    todayPower = multiply_and_sum(split_and_return(data['stats']['daily']['panelVoltage'], evenDay), split_and_return(data['stats']['daily']['panelCurrent'], evenDay))
    todayCharge =  multiply_and_sum(split_and_return(data['stats']['daily']['batteryVoltage'], evenDay), split_and_return(data['stats']['daily']['batteryVoltage'], evenDay))
    
    data['stats']['monthly']['powerProduction'][date] = round(todayPower,2)
    data['stats']['monthly']['batteryCharge'][date] = round(todayCharge,2)
    print("monthly",todayPower,todayCharge)
    
    with open('pipe.json', 'w') as file:
        json.dump(data, file, indent=4)

def read_file_content(file_path):
    """Read and return the file content, None if file not found."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None

def has_file_content_changed(file_path, last_content):
    """Check if the file's content has changed."""
    current_content = read_file_content(file_path)
    return current_content != last_content, current_content

def check_updates_refresh_json_data(file_path):
    """Check if settings.toggleUpdate is true in the JSON file."""
    content = read_file_content(file_path)
    if content:
        global json_data
        try:
            json_data = json.loads(content)
            return json_data.get('settings', {}).get('toggleUpdate', False)
        except json.JSONDecodeError:
            print("Error decoding the JSON file.")
    return False

def watch_file(file_path, interval=1):
    """Watches a file for content changes and toggleUpdates status."""
    last_content = read_file_content(file_path)
    if last_content is None:
        return

    while True:
        changed, last_content = has_file_content_changed(file_path, last_content)
        if changed:
            print(f"File {file_path} content has been modified.")
            global toggled
            if check_updates_refresh_json_data(file_path):
                toggled = True
                # Modify the json here
                print("settings.toggleUpdate is enabled.")
                log_readings()
                # Save the changes to the file
                # save_json(file_path, json_data)
            else:
                toggled = False
                
        time.sleep(interval)

def start_watching(file_path):
    """Starts watching the file on a separate thread."""
    threading.Thread(target=watch_file, args=(file_path,), daemon=True).start()
    print(f"Started watching {file_path} on a separate thread.")

    
def run_scheduler():
    # Schedule the function to run every 10 minutes
    
    schedule.every(5).minutes.do(log_daily_stats)

    # Schedule the function to run every 24 hours
    schedule.every().day.at("18:00").do(log_monthly_stats)

    # Run the scheduler in a loop
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

file_to_watch = "pipe.json"
start_watching(file_to_watch)
# Main program continues here
try:
    while True:
        # Mengatur ulang tampilan OLED
        draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

        # Memulai PWM
        pwm1.start(nilaipwm1)
        pwm2.start(nilaipwm2)

        # Mengumpulkan data arus dan tegangan
        jumlaharus, jumlahtegangan = 0, 0
        jumlaharus2, jumlahtegangan2 = 0, 0
        for _ in range(10):
            arus1 = max(0, (0.123 - 2.5265) / 0.185 * 1.65)
            arus2 = max(0, (0.123 - 2.5265) / 0.185 * 1.65)
            tegangan1 = max(0, 0.123 * 5)
            tegangan2 = max(0, 0.123 * 5)
            jumlaharus += arus1
            jumlaharus2 += arus2
            jumlahtegangan += tegangan1
            jumlahtegangan2 += tegangan2
            time.sleep(0.01)
        """  for _ in range(10):
            arus1 = random.uniform(0.5, 1.5)
            arus2 = random.uniform(0.5, 1.5)
            tegangan1 = random.uniform(6, 15)
            tegangan2 = random.uniform(10, 13)
            jumlaharus += arus1
            jumlahtegangan += tegangan1
            time.sleep(0.01) """
        # Menghitung rata-rata dan daya
        arus1 = jumlaharus / 10.0
        arus2 = jumlaharus2 / 10.0
        tegangan1 = jumlahtegangan / 10.0
        tegangan2 = jumlahtegangan2 / 10.0
        daya1 = arus1 * tegangan1
        daya2 = arus2 * tegangan2
        # Logika MPPT untuk menyesuaikan nilai PWM
        if mode == "BUCK":
            current_limit = buck_current_threshold
            if tegangan2 >= absorption_voltage_threshold:
                mode == "ABSORPTION"   
        elif mode == "ABSORPTION":
            voltage_limit = absorption_voltage_threshold
            if arus2 <= absorption_current_treshold:
                mode = "FLOAT"
        elif mode == "FLOAT":
            voltage_limit = float_voltage_threshold
            current_limit = absorption_current_treshold
            if arus2 >= (absorption_current_treshold + 0.1):
                mode = "BUCK"
                
        if daya1 - dayaSebelumnya >= 0.5 or daya1 == dayaSebelumnya:
            if nilaipwm1 < 100 and tegangan2 < voltage_limit and arus2 < current_limit:
                nilaipwm1 += 5
            elif nilaipwm2 < 100 and tegangan1 > teganganSebelumnya and tegangan2 < voltage_limit:
                nilaipwm2 += 2
            elif nilaipwm2 > 1:
                nilaipwm2 -= 2
        elif dayaSebelumnya - daya1 > 0.5:
            if nilaipwm1 >= 100 and tegangan1 > teganganSebelumnya and tegangan2 < voltage_limit:
                nilaipwm2 += 2
            elif nilaipwm2 > 1:
                nilaipwm2 -= 2
            elif nilaipwm1 > 5:
                nilaipwm1 -= 5

        # Check if the new value is significantly different from all existing values
        if not V_buffer or is_significantly_different(tegangan1, V_buffer, threshold_V):
            #Add the new values to the buffers
            I_index = add_to_buffer(I_buffer, I_index, round(arus1,2), max_size)
            V_index = add_to_buffer(V_buffer, V_index, round(tegangan1,2), max_size)
            
        if not I_buffer or is_significantly_different(arus1, I_buffer, threshold_I):
            I_index = add_to_buffer(I_buffer, I_index, round(arus1,2), max_size)
            V_index = add_to_buffer(V_buffer, V_index, round(tegangan1,2), max_size)

        # Memperbarui nilai sebelumnya
        # print("daya",dayaSebelumnya,teganganSebelumnya,arus1,tegangan1,arus2,tegangan2,nilaipwm1,nilaipwm2)

        # Menampilkan data pada OLED
        draw.text((0, 0), "Vp: " + str(round(tegangan1, 2)), font=font, fill=255)
        draw.text((0, 16), "Ip: " + str(round(arus1, 2)), font=font, fill=255)
        draw.text((0, 32), "Pp: " + str(round(daya1, 2)), font=font, fill=255)
        draw.text((0, 48), "G " + str(nilaipwm1), font=font, fill=255)
        draw.text((45, 48), str(nilaipwm2), font=font, fill=255)
        
        teganganFull, teganganMin = 14, 10
        presentase = calculate_battery_percentage(tegangan2)
        draw.text((70, 0), "Vb: " + str(round(tegangan2, 2)), font=font, fill=255)
        draw.text((70, 16), "Ib: " + str(round(arus2, 2)), font=font, fill=255)      
        draw.text((70, 32), "Tb: " + str(round(read_temp())) + "°C", font=font, fill=255)

        draw.text((70, 48), "B: " + str(round(presentase, 2)) + "%", font=font, fill=255)
        oled.image(image)
        oled.show()
        print("Solar,","V",(round(tegangan1, 2)),"I",(round(arus1, 2)),"P",(round(daya1, 2)),"adc1",(round(0.123, 2)),"adc2",(round(0.123, 2)),"pwm1",round(nilaipwm1, 2))
        print("Bat  ,","V",(round(tegangan2, 2)),"I",(round(arus2, 2)),"P",(round(dayaSebelumnya, 2)),"adc3",(round(0.123, 2)),"adc4",(round(0.123, 2)),"pwm2",round(nilaipwm2, 2))
        dayaSebelumnya, teganganSebelumnya = daya1, tegangan1

except KeyboardInterrupt:
    pass
finally:
    pwm1.stop()
    pwm2.stop()


