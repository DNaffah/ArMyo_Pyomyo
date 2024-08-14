import multiprocessing
import queue
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from scipy.signal import butter, filtfilt
from scipy.fft import fft, fftfreq
from pyomyo import Myo, emg_mode

print("Press ctrl+pause/break to stop")

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
    m = Myo(mode=emg_mode.PREPROCESSED)
    m.connect()

    def add_to_queue(quat, acc, gyro):
        imu_data = [quat, acc, gyro]
        q.put(imu_data)

    def print_battery(bat):
        print("Battery level:", bat)

    m.set_leds([128, 0, 0], [128, 0, 0])
    m.vibrate(1)
    m.add_battery_handler(print_battery)
    m.add_imu_handler(add_to_queue)

    while True:
        try:
            m.run()
        except:
            print("Worker Stopped")
            quit()

# ------------ Plot Setup ---------------
QUEUE_SIZE = 100
subplots = []
lines = []
annotations = []

plt.rcParams["figure.figsize"] = (10, 16)
fig, subplots = plt.subplots(3, 1, figsize=(10, 12))
fig.canvas.manager.set_window_title("IMU Data Plot")
fig.tight_layout()

# Initialize lines and annotations
acc_lines = [subplots[0].plot(range(QUEUE_SIZE), [0] * QUEUE_SIZE, label=axis)[0] for axis in ['Acc_x', 'Acc_y', 'Acc_z']]
gyro_lines = [subplots[1].plot(range(QUEUE_SIZE), [0] * QUEUE_SIZE, label=axis)[0] for axis in ['Gyro_x', 'Gyro_y', 'Gyro_z']]
quat_lines = [subplots[2].plot(range(QUEUE_SIZE), [0] * QUEUE_SIZE, label=axis)[0] for axis in ['Quat_x', 'Quat_y', 'Quat_z']]

for ax in subplots:
    ax.legend()
    annotations.append(ax.text(0.8, 0.9, '', transform=ax.transAxes, fontsize=12))

quat_w_annotation = subplots[2].text(0.8, 0.8, '', transform=subplots[2].transAxes, fontsize=12)
gyro_x_annotation = subplots[1].text(0.8, 0.8, '', transform=subplots[1].transAxes, fontsize=12)
gyro_y_annotation = subplots[1].text(0.8, 0.75, '', transform=subplots[1].transAxes, fontsize=12)
gyro_z_annotation = subplots[1].text(0.8, 0.7, '', transform=subplots[1].transAxes, fontsize=12)

imu_queue = queue.Queue(QUEUE_SIZE)

# Butterworth filter function
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data, axis=0)
    return y

def calculate_frequency(data, fs):
    N = len(data)
    yf = fft(data)
    xf = fftfreq(N, 1/fs)[:N//2]
    idx = np.argmax(2.0/N * np.abs(yf[:N//2]))
    return xf[idx]

def filter_gyro_noise(gyro_data, threshold=50):
    gyro_data_filtered = np.copy(gyro_data)
    gyro_data_filtered[np.abs(gyro_data) < threshold] = 0
    return gyro_data_filtered

def animate(i):
    while not q.empty():
        imu = list(q.get())
        quat, acc, gyro = imu

        if imu_queue.full():
            imu_queue.get()
        imu_queue.put((quat, acc, gyro))

    quats = []
    accs = []
    gyros = []

    for quat, acc, gyro in list(imu_queue.queue):
        quats.append(quat)
        accs.append(acc)
        gyros.append(gyro)

    if imu_queue.full():
        acc_data = np.array(accs)
        gyro_data = np.array(gyros)
        quat_data = np.array(quats)

        # Apply filters
        fs = 100  # Sample rate
        acc_data_filtered = butter_lowpass_filter(acc_data, 2, fs)
        quat_data_filtered = butter_lowpass_filter(quat_data[:, 1:], 2, fs)
        gyro_data_filtered = butter_lowpass_filter(gyro_data, 1, fs)  # Más agresivo para el giroscopio
        gyro_data_filtered = filter_gyro_noise(gyro_data_filtered)  # Filtro de 50 unidades

        # Update lines for acceleration
        for i, line in enumerate(acc_lines):
            line.set_ydata(acc_data_filtered[:, i])
            subplots[0].relim()
            subplots[0].autoscale_view()

        # Update lines for gyroscope with noise filter
        for i, line in enumerate(gyro_lines):
            line.set_ydata(gyro_data_filtered[:, i])
            subplots[1].relim()
            subplots[1].autoscale_view()

        # Update lines for quaternion (excluding quat_w)
        for i, line in enumerate(quat_lines):
            line.set_ydata(quat_data_filtered[:, i])
            subplots[2].relim()
            subplots[2].autoscale_view()

        # Update annotation for quat_w
        quat_w_annotation.set_text(f'Quat_w: {quat_data[-1, 0]}')

        # Update annotations for gyro axes
        gyro_x_annotation.set_text(f'Gyro_x: {gyro_data_filtered[-1, 0]:.2f}')
        gyro_y_annotation.set_text(f'Gyro_y: {gyro_data_filtered[-1, 1]:.2f}')
        gyro_z_annotation.set_text(f'Gyro_z: {gyro_data_filtered[-1, 2]:.2f}')

        # Calculate and update frequency annotations
        acc_freq = calculate_frequency(acc_data[:, 0], fs)
        gyro_freq = calculate_frequency(gyro_data_filtered[:, 0], fs)
        quat_freq = calculate_frequency(quat_data[:, 1], fs)

        annotations[0].set_text(f'Freq: {acc_freq:.2f} Hz')
        annotations[1].set_text(f'Freq: {gyro_freq:.2f} Hz')
        annotations[2].set_text(f'Freq: {quat_freq:.2f} Hz')

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', force=True)
    p = multiprocessing.Process(target=worker, args=(q,))
    p.start()

    while q.empty():
        continue

    anim = animation.FuncAnimation(fig, animate, blit=False, interval=50)

    def on_close(event):
        p.terminate()
        raise KeyboardInterrupt
        print("On close has ran")

    fig.canvas.mpl_connect('close_event', on_close)

    try:
        plt.show()
    except KeyboardInterrupt:
        plt.close()
        p.close()
        quit()
