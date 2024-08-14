import multiprocessing
import queue
import numpy as np
import os
from scipy.signal import butter, filtfilt
from pyomyo import Myo, emg_mode

print("Press ctrl+pause/break to stop")

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()
data_buffer = []
normalized_buffer = None

def worker(q):
    m = Myo(mode=emg_mode.PREPROCESSED)
    m.connect()

    def add_to_queue(quat, acc, gyro):
        q.put((quat, acc, gyro))

    def print_battery(bat):
        print("Battery level:", bat)

    m.set_leds([128, 0, 0], [128, 0, 0])
    m.vibrate(1)
    m.add_battery_handler(print_battery)
    m.add_imu_handler(lambda quat, acc, gyro: add_to_queue(quat, acc, gyro))

    while True:
        try:
            m.run()
        except:
            print("Worker Stopped")
            quit()

# Butterworth filter function
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data, axis=0)
    return y

def normalize(data, prev_normalized, tolerance=0.01):
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    std[std < tolerance] = 1  # Prevent division by zero with a tolerance threshold

    normalized_data = (data - mean) / std

    if prev_normalized is not None and np.all(std < tolerance):
        normalized_data = prev_normalized

    return normalized_data

def cls():
    # Clear the screen in a cross platform way
    os.system('cls' if os.name == 'nt' else 'clear')

def display_annotations(quat_data, quat_data_normalized):
    # Display quaternion data before normalization
    print("Quaternion Data Before Normalization:")
    print(f"Quat_w: {quat_data[-1, 0]:.2f}")
    print(f"Quat_x: {quat_data[-1, 1]:.2f}")
    print(f"Quat_y: {quat_data[-1, 2]:.2f}")
    print(f"Quat_z: {quat_data[-1, 3]:.2f}")

    # Display quaternion data after normalization
    print("\nQuaternion Data After Normalization:")
    print(f"Quat_w_norm: {quat_data_normalized[-1, 0]:.2f}")
    print(f"Quat_x_norm: {quat_data_normalized[-1, 1]:.2f}")
    print(f"Quat_y_norm: {quat_data_normalized[-1, 2]:.2f}")
    print(f"Quat_z_norm: {quat_data_normalized[-1, 3]:.2f}")

def process_data():
    global normalized_buffer
    while True:
        if not q.empty():
            quat, acc, gyro = q.get()
            if quat is not None and acc is not None and gyro is not None:
                data_buffer.append(quat)
                
                if len(data_buffer) >= 20:  # Ensure we have enough data for the filter
                    quat_data = np.array(data_buffer[-20:])

                    # Apply lowpass filter to the quaternion data
                    fs = 100  # Sample rate
                    quat_data_filtered = butter_lowpass_filter(quat_data, 2, fs)

                    # Normalize the filtered quaternion data
                    quat_data_normalized = normalize(quat_data_filtered, normalized_buffer)
                    normalized_buffer = quat_data_normalized

                    # Display annotations
                    cls()  # Clear the screen
                    display_annotations(quat_data_filtered, quat_data_normalized)

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', force=True)
    p = multiprocessing.Process(target=worker, args=(q,))
    p.start()

    try:
        process_data()
    except KeyboardInterrupt:
        p.terminate()
        p.join()
        print("Quitting")
