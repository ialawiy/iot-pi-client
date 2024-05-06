import board
import RPi.GPIO as GPIO
import time
import busio
import digitalio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import json
import threading

from datetime import datetime

import schedule

now = datetime.now()
five_minutes_start = (now.hour * 60 + now.minute) // 10
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

# Inisialisasi I2C dan objek ADS1115 untuk pembacaan analog
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# Mendefinisikan channel input analog
adcArus = AnalogIn(ads, ADS.P0)
adcTegangan = AnalogIn(ads, ADS.P1)
adcArus2 = AnalogIn(ads, ADS.P2)
adcTegangan2 = AnalogIn(ads, ADS.P3)

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

# Function to create a new circular buffer
def create_circular_buffer(size):
    return [None] * size, 0  # Buffer list and current index

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
   
def log_readings():
    with open('pipe.json', 'r') as file:
        data = json.load(file)
    
    data['readings']['batteryCurrent'] = arus2
    data['readings']['panelCurrent'] = arus1
    data['readings']['batteryVoltage'] = tegangan2
    data['readings']['panelVoltage'] = tegangan1    
    
    data['stats']['curveIV']['voltage'] = V_buffer
    data['stats']['curveIV']['current'] = I_buffer
    data['details']['lastUpdate'] = datetime.now()
    
    data['settings']['toggleUpdate'] = False
    
    # Write the modified data back to the file
    with open('pipe.json', 'w') as file:
        json.dump(data, file, indent=4)    
    
def log_daily_stats():
    now = datetime.now()
    current_time = now.time()
    if current_time >= datetime.time(6, 0) and current_time <= datetime.time(18, 0):
        five_minutes = (now.hour * 60 + now.minute) // 10
        # Read the JSON file
        with open('pipe.json', 'r') as file:
            data = json.load(file)
        if(now.day%2):
            five_minutes += 144
        # Modify the data
        # For example, add a new key-value pair
        data['readings']['batteryCurrent'] = arus2
        data['readings']['panelCurrent'] = arus1
        data['readings']['batteryVoltage'] = tegangan2
        data['readings']['panelVoltage'] = tegangan1    # Write the modified data back to the file
        
        data['stats']['daily']['batteryCurrent'][five_minutes] = arus2
        data['stats']['daily']['panelCurrent'][five_minutes] = arus1
        data['stats']['daily']['batteryVoltage'][five_minutes] = tegangan2
        data['stats']['daily']['panelVoltage'][five_minutes] = tegangan1    # Write the modified data back to the file
        
        data['settings']['toggleUpdate'] = False    # Write the modified data back to the file
        data['details']['lastUpdate'] = now
        
        with open('pipe.json', 'w') as file:
            json.dump(data, file, indent=4)
        
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
    data['details']['lastUpdate'] = now
    data['stats']['monthly']['powerProduction'][date] = multiply_and_sum(split_and_return(data['stats']['daily']['panelVoltage'], evenDay), split_and_return(data['stats']['daily']['panelCurrent'], evenDay))
    data['stats']['monthly']['batteryCharge'][date] = multiply_and_sum(split_and_return(data['stats']['daily']['batteryVoltage'], evenDay), split_and_return(data['stats']['daily']['batteryVoltage'], evenDay))
    with open('pipe.json', 'w') as file:
        json.dump(data, file, indent=4)


def save_json(file_path, data):
    """Save the JSON object to a file."""
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


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
    schedule.every().day.at("18:01").do(log_monthly_stats)

    # Run the scheduler in a loop
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

if __name__ == "__main__":
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
            for _ in range(10):
                arus1 = max(0, (adcArus.voltage - 2.5265) / 0.185 * 1.16)
                arus2 = max(0, (adcArus2.voltage - 2.5265) / 0.185 * 1.16)
                tegangan1 = max(0, adcTegangan.voltage * 5.302 * 1.16)
                tegangan2 = max(0, adcTegangan2.voltage * 5.302 * 1.16)
                jumlaharus += arus1
                jumlahtegangan += tegangan1
                time.sleep(0.01)
                
            # Menghitung rata-rata dan daya
            arus1 = jumlaharus / 10.0
            tegangan1 = jumlahtegangan / 10.0
            daya1 = arus1 * tegangan1

            # Logika MPPT untuk menyesuaikan nilai PWM
            if daya1 - dayaSebelumnya >= 0.5 or daya1 == dayaSebelumnya:
                if nilaipwm1 < 100:
                    nilaipwm1 += 5
                elif nilaipwm2 < 100 and tegangan1 > teganganSebelumnya:
                    nilaipwm2 += 2
                elif nilaipwm2 > 1:
                    nilaipwm2 -= 2
            elif dayaSebelumnya - daya1 > 0.5:
                if nilaipwm1 >= 100 and tegangan1 > teganganSebelumnya:
                    nilaipwm2 += 2
                elif nilaipwm2 > 1:
                    nilaipwm2 -= 2
                elif nilaipwm1 > 5:
                    nilaipwm1 -= 5
            # Check if the new value is significantly different from all existing values
            if not V_buffer or is_significantly_different(tegangan1, V_buffer, threshold_V):
                # Add the new values to the buffers
                I_index = add_to_buffer(I_buffer, I_index, arus1, max_size)
                V_index = add_to_buffer(V_buffer, V_index, tegangan1, max_size)
                
            if not I_buffer or is_significantly_different(arus1, I_buffer, threshold_I):
                I_index = add_to_buffer(I_buffer, I_index, arus1, max_size)
                V_index = add_to_buffer(V_buffer, V_index, tegangan1, max_size)

            # Memperbarui nilai sebelumnya
            dayaSebelumnya, teganganSebelumnya = daya1, tegangan1

            # Menampilkan data pada OLED
            draw.text((0, 0), "V: " + str(round(tegangan1, 2)), font=font, fill=255)
            draw.text((0, 16), "I: " + str(round(arus1, 2)), font=font, fill=255)
            draw.text((0, 32), "P: " + str(round(daya1, 2)), font=font, fill=255)
            teganganFull, teganganMin = 19, 12
            presentase = ((tegangan2 - teganganMin) / (teganganFull - teganganMin)) * 100
            draw.text((60, 0), "B: " + str(round(presentase, 2)) + "%", font=font, fill=255)
            oled.image(image)
            oled.show()

    except KeyboardInterrupt:
        pass
    finally:
        pwm1.stop()
        pwm2.stop()
