import multiprocessing
import queue
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from scipy.signal import butter, filtfilt
from pyomyo import Myo, emg_mode

print("Press ctrl+pause/break to stop")

# ------------ Myo Setup ---------------
q = multiprocessing.Queue()

def worker(q):
    m = Myo(mode=emg_mode.PREPROCESSED)
    m.connect()

    def add_to_queue(emg, movement, quat, acc, gyro):
        q.put((emg, quat, acc, gyro))

    def print_battery(bat):
        print("Battery level:", bat)

    m.set_leds([128, 0, 0], [128, 0, 0])
    m.vibrate(1)
    m.add_battery_handler(print_battery)
    m.add_emg_handler(lambda emg, movement: add_to_queue(emg, movement, None, None, None))
    m.add_imu_handler(lambda quat, acc, gyro: add_to_queue(None, None, quat, acc, gyro))

    while True:
        try:
            m.run()
        except:
            print("Worker Stopped")
            quit()

# ------------ Plot Setup ---------------
QUEUE_SIZE = 100

# EMG plot setup
SENSORS_EMG = 8
subplots_emg = []
lines_emg = []
annotations_emg = []

plt.rcParams["figure.figsize"] = (10, 16)
fig_emg, subplots_emg = plt.subplots(SENSORS_EMG, 1)
fig_emg.canvas.manager.set_window_title("8 Channel EMG plot")
fig_emg.tight_layout()

# IMU plot setup
subplots_imu = []
lines_imu = []
annotations_imu = []

fig_imu, subplots_imu = plt.subplots(3, 1, figsize=(10, 12))
fig_imu.canvas.manager.set_window_title("IMU Data Plot")
fig_imu.tight_layout()

# Initialize EMG lines and annotations
name = "tab10"
cmap = plt.get_cmap(name)
colors = cmap.colors

for i in range(SENSORS_EMG):
    ch_line, = subplots_emg[i].plot(range(QUEUE_SIZE), [0] * QUEUE_SIZE, color=colors[i])
    lines_emg.append(ch_line)
    annotation = subplots_emg[i].text(0.8, 0.9, '', transform=subplots_emg[i].transAxes, fontsize=12)
    annotations_emg.append(annotation)

# Initialize IMU lines and annotations
acc_lines = [subplots_imu[0].plot(range(QUEUE_SIZE), [0] * QUEUE_SIZE, label=axis)[0] for axis in ['Acc_x', 'Acc_y', 'Acc_z']]
gyro_lines = [subplots_imu[1].plot(range(QUEUE_SIZE), [0] * QUEUE_SIZE, label=axis)[0] for axis in ['Gyro_x', 'Gyro_y', 'Gyro_z']]
quat_lines = [subplots_imu[2].plot(range(QUEUE_SIZE), [0] * QUEUE_SIZE, label=axis)[0] for axis in ['Quat_x', 'Quat_y', 'Quat_z']]

for ax in subplots_imu:
    ax.legend()
    annotations_imu.append(ax.text(0.8, 0.9, '', transform=ax.transAxes, fontsize=12))

quat_w_annotation = subplots_imu[2].text(0.8, 0.8, '', transform=subplots_imu[2].transAxes, fontsize=12)

# Annotations for quaternion x, y, z
quat_x_annotation = subplots_imu[2].text(0.2, 0.8, '', transform=subplots_imu[2].transAxes, fontsize=12)
quat_y_annotation = subplots_imu[2].text(0.4, 0.8, '', transform=subplots_imu[2].transAxes, fontsize=12)
quat_z_annotation = subplots_imu[2].text(0.6, 0.8, '', transform=subplots_imu[2].transAxes, fontsize=12)

emg_queue = queue.Queue(QUEUE_SIZE)
imu_queue = queue.Queue(QUEUE_SIZE)

# Butterworth filter function
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data, axis=0)
    return y

def filter_emg_noise(emg_data, threshold=60):
    emg_data_filtered = np.copy(emg_data)
    emg_data_filtered[np.abs(emg_data) < threshold] = 0
    return emg_data_filtered

def filter_gyro_noise(gyro_data, threshold=50):
    gyro_data_filtered = np.copy(gyro_data)
    gyro_data_filtered[np.abs(gyro_data) < threshold] = 0
    return gyro_data_filtered

def animate(i):
    # Myo Plot
    while not q.empty():
        emg, quat, acc, gyro = q.get()
        if emg is not None:
            if emg_queue.full():
                emg_queue.get()
            emg_queue.put(emg)
        if quat is not None and acc is not None and gyro is not None:
            if imu_queue.full():
                imu_queue.get()
            imu_queue.put((quat, acc, gyro))

    # Update EMG plot
    if emg_queue.full():
        channels = np.array(list(emg_queue.queue))
        fs = 200  # Sample rate
        channels_filtered = butter_lowpass_filter(channels, 5, fs)
        channels_filtered = filter_emg_noise(channels_filtered)
        for i in range(SENSORS_EMG):
            channel = channels_filtered[:, i]
            lines_emg[i].set_ydata(channel)
            subplots_emg[i].set_ylim(0, max(100, max(channel)))
            annotations_emg[i].set_text(f'EMG_{i}: {channel[-1]}')

    # Update IMU plot
    if imu_queue.full():
        quats = []
        accs = []
        gyros = []
        for quat, acc, gyro in list(imu_queue.queue):
            quats.append(quat)
            accs.append(acc)
            gyros.append(gyro)

        acc_data = np.array(accs)
        gyro_data = np.array(gyros)
        quat_data = np.array(quats)

        fs = 100  # Sample rate
        acc_data_filtered = butter_lowpass_filter(acc_data, 2, fs)
        gyro_data_filtered = filter_gyro_noise(butter_lowpass_filter(gyro_data, 2, fs))
        quat_data_filtered = butter_lowpass_filter(quat_data[:, 1:], 2, fs)

        # Update lines for acceleration
        for i, line in enumerate(acc_lines):
            line.set_ydata(acc_data_filtered[:, i])
            subplots_imu[0].relim()
            subplots_imu[0].autoscale_view()

        # Update lines for gyroscope with noise filter
        for i, line in enumerate(gyro_lines):
            line.set_ydata(gyro_data_filtered[:, i])
            subplots_imu[1].relim()
            subplots_imu[1].autoscale_view()
            annotations_imu[1].set_text(f'Gyro_{i}: {gyro_data_filtered[-1, i]:.2f}')

        # Update lines for quaternion (excluding quat_w)
        for i, line in enumerate(quat_lines):
            line.set_ydata(quat_data_filtered[:, i])
            subplots_imu[2].relim()
            subplots_imu[2].autoscale_view()

        # Update annotation for quat_w
        quat_w_annotation.set_text(f'Quat_w: {quat_data[-1, 0]}')
        quat_x_annotation.set_text(f'Quat_x: {quat_data_filtered[-1, 0]:.2f}')
        quat_y_annotation.set_text(f'Quat_y: {quat_data_filtered[-1, 1]:.2f}')
        quat_z_annotation.set_text(f'Quat_z: {quat_data_filtered[-1, 2]:.2f}')

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', force=True)
    p = multiprocessing.Process(target=worker, args=(q,))
    p.start()

    while q.empty():
        continue

    anim_imu = animation.FuncAnimation(fig_imu, animate, blit=False, interval=50)
    anim_emg = animation.FuncAnimation(fig_emg, animate, blit=False, interval=50)

    def on_close(event):
        p.terminate()
        raise KeyboardInterrupt
        print("On close has ran")

    fig_imu.canvas.mpl_connect('close_event', on_close)
    fig_emg.canvas.mpl_connect('close_event', on_close)

    try:
        plt.show()
    except KeyboardInterrupt:
        plt.close()
        p.close()
        quit()
