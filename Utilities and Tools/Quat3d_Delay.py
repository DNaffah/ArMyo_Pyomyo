import multiprocessing
import queue
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
from scipy.signal import butter, filtfilt
from scipy.spatial.transform import Rotation as R
from pyomyo import Myo, emg_mode
import time
import os

print("Press ctrl+pause/break to stop")

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
    m = Myo(mode=emg_mode.PREPROCESSED)
    m.connect()

    def add_to_queue(emg, movement, quat, acc, gyro):
        q.put((quat, acc, gyro))

    def print_battery(bat):
        print("Battery level:", bat)

    m.set_leds([128, 0, 0], [128, 0, 0])
    m.vibrate(1)
    m.add_battery_handler(print_battery)
    m.add_imu_handler(lambda quat, acc, gyro: add_to_queue(None, None, quat, acc, gyro))

    while True:
        try:
            m.run()
        except:
            print("Worker Stopped")
            quit()

# ------------ Plot Setup ---------------
QUEUE_SIZE = 100

# IMU plot setup
fig_imu = plt.figure(figsize=(10, 10))
ax_imu = fig_imu.add_subplot(111, projection='3d')
fig_imu.canvas.manager.set_window_title("Quaternion Data Plot")

quat_w_annotation = ax_imu.text2D(0.05, 0.95, '', transform=ax_imu.transAxes, fontsize=12)
quat_x_annotation = ax_imu.text2D(0.05, 0.90, '', transform=ax_imu.transAxes, fontsize=12)
quat_y_annotation = ax_imu.text2D(0.05, 0.85, '', transform=ax_imu.transAxes, fontsize=12)
quat_z_annotation = ax_imu.text2D(0.05, 0.80, '', transform=ax_imu.transAxes, fontsize=12)

imu_queue = queue.Queue(QUEUE_SIZE)

# Butterworth filter function
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data, axis=0)
    return y

def normalize_quaternions(data):
    norms = np.linalg.norm(data[:, 1:], axis=1, keepdims=True)
    norms[norms == 0] = 1  # Prevent division by zero
    return np.hstack((data[:, [0]], data[:, 1:] / norms))

def rotate_quaternions(data, rotation):
    r = R.from_quat(rotation)
    rotated_data = r.apply(data[:, 1:])
    return np.hstack((data[:, [0]], rotated_data))

def duplicate_quaternions(data):
    # Duplicar e invertir quaterniones para simular un círculo completo
    duplicated_data = np.vstack((data, -data))
    return duplicated_data

quats = []

def animate(i):
    while not q.empty():
        quat, acc, gyro = q.get()
        if quat is not None and acc is not None and gyro is not None:
            if len(quats) >= QUEUE_SIZE:
                quats.pop(0)
            quats.append(quat)

    if len(quats) >= 20:  # Ensure there are enough points for the filter
        quat_data = np.array(quats)

        # Apply lowpass filter to the quaternion data
        fs = 100  # Sample rate
        quat_data_filtered = butter_lowpass_filter(quat_data[:, 1:], 2, fs)

        # Normalize the filtered quaternion data
        quat_data_filtered = np.hstack((quat_data[:, [0]], quat_data_filtered))
        quat_data_normalized = normalize_quaternions(quat_data_filtered)

        # Define the rotation quaternion for alignment
        theta = np.pi / (64/15)  # Adjust this angle as needed ## Touching
        rotation = [np.cos(theta / 2), 0, np.sin(theta / 2), 0]

        # Rotate the normalized quaternion data
        quat_data_normalized_rotated = rotate_quaternions(quat_data_normalized, rotation)

        # Duplicate the data to simulate a full circle
        quat_data_final = duplicate_quaternions(quat_data_normalized_rotated)

        # Update annotations for quat_w, quat_x, quat_y, quat_z
        quat_w_annotation.set_text(f'Quat_w: {quat_data[-1, 0]:.2f}')
        quat_x_annotation.set_text(f'Quat_x: {quat_data_final[-1, 1]:.2f}')
        quat_y_annotation.set_text(f'Quat_y: {quat_data_final[-1, 2]:.2f}')
        quat_z_annotation.set_text(f'Quat_z: {quat_data_final[-1, 3]:.2f}')

        # Clear previous points
        # ax_imu.cla()

        # Plot all normalized quaternion x, y, z points
        ax_imu.scatter(quat_data_final[:, 1], quat_data_final[:, 2], quat_data_final[:, 3], c='r', marker='o')

        # Set labels for axes
        ax_imu.set_xlabel('X Axis')
        ax_imu.set_ylabel('Y Axis')
        ax_imu.set_zlabel('Z Axis')

        # Set limits for axes
        ax_imu.set_xlim([-1, 1])
        ax_imu.set_ylim([-1, 1])
        ax_imu.set_zlim([-1, 1])

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', force=True)
    p = multiprocessing.Process(target=worker, args=(q,))
    p.start()

    time.sleep(5)  # Wait for 5 segundos antes de comenzar a graficar

    while q.empty():
        continue

    anim_imu = animation.FuncAnimation(fig_imu, animate, blit=False, interval=50, save_count=100)

    def on_close(event):
        p.terminate()
        raise KeyboardInterrupt
        print("On close has ran")

    fig_imu.canvas.mpl_connect('close_event', on_close)

    try:
        plt.show()
    except KeyboardInterrupt:
        plt.close()
        p.close()
        quit()
