import multiprocessing
import queue
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
from scipy.signal import butter, filtfilt
from pyomyo import Myo, emg_mode

print("Press ctrl+pause/break to stop")

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

# Quaternion signals plot setup
fig_quat, subplots_quat = plt.subplots(2, 1, figsize=(10, 10))
fig_quat.canvas.manager.set_window_title("Quaternion Signals Plot")
fig_quat.tight_layout()

# Initialize lines for quaternion signals before and after normalization
lines_quat_before = [subplots_quat[0].plot(range(QUEUE_SIZE), [0] * QUEUE_SIZE, label=f'Quat_{axis}')[0] for axis in ['x', 'y', 'z']]
lines_quat_after = [subplots_quat[1].plot(range(QUEUE_SIZE), [0] * QUEUE_SIZE, label=f'Quat_{axis}_norm')[0] for axis in ['x', 'y', 'z']]

annotations_quat_before = [subplots_quat[0].text(0.8, 0.9 - i * 0.05, '', transform=subplots_quat[0].transAxes, fontsize=12) for i in range(3)]
annotations_quat_after = [subplots_quat[1].text(0.8, 0.9 - i * 0.05, '', transform=subplots_quat[1].transAxes, fontsize=12) for i in range(3)]

for ax in subplots_quat:
    ax.legend()

quat_w_annotation_before = subplots_quat[0].text(0.8, 0.1, '', transform=subplots_quat[0].transAxes, fontsize=12)
quat_w_annotation_after = subplots_quat[1].text(0.8, 0.1, '', transform=subplots_quat[1].transAxes, fontsize=12)

imu_queue = queue.Queue(QUEUE_SIZE)

# Butterworth filter function
def butter_lowpass_filter(data, cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data, axis=0)
    return y

def normalize_quaternions(data):
    norm = np.linalg.norm(data[:, 1:], axis=1, keepdims=True)
    return data[:, 1:] / norm

def animate(i):
    # Myo Plot
    while not q.empty():
        quat, acc, gyro = q.get()
        if quat is not None and acc is not None and gyro is not None:
            if imu_queue.full():
                imu_queue.get()
            imu_queue.put((quat, acc, gyro))

    # Update IMU plot
    if imu_queue.full():
        quats = []
        for quat, acc, gyro in list(imu_queue.queue):
            quats.append(quat)

        quat_data = np.array(quats)

        # Apply lowpass filter to the quaternion data
        fs = 100  # Sample rate
        quat_data_filtered = butter_lowpass_filter(quat_data[:, 1:], 2, fs)

        # Normalize the filtered quaternion data
        quat_data_normalized = normalize_quaternions(np.hstack((quat_data[:, [0]], quat_data_filtered)))

        # Clear previous points
        ax_imu.cla()
        ax_imu.set_xlim([-2, 2])
        ax_imu.set_ylim([-2, 2])
        ax_imu.set_zlim([-2, 2])

        # Plot only the last normalized quaternion x, y, z as a point
        ax_imu.scatter(quat_data_normalized[-1, 0], quat_data_normalized[-1, 1], quat_data_normalized[-1, 2], c='r', marker='o')

        # Update annotations for quat_w
        quat_w_annotation_before.set_text(f'Quat_w: {quat_data[-1, 0]:.2f}')
        quat_w_annotation_after.set_text(f'Quat_w_norm: {quat_data_normalized[-1, 0]:.2f}')

        # Update quaternion signals plot before normalization
        for i, line in enumerate(lines_quat_before):
            line.set_ydata(quat_data[:, i+1])
            subplots_quat[0].relim()
            subplots_quat[0].autoscale_view()
            annotations_quat_before[i].set_text(f'Quat_{["x", "y", "z"][i]}: {quat_data[-1, i+1]:.2f}')

        # Update quaternion signals plot after normalization
        for i, line in enumerate(lines_quat_after):
            line.set_ydata(quat_data_normalized[:, i])
            subplots_quat[1].relim()
            subplots_quat[1].autoscale_view()
            annotations_quat_after[i].set_text(f'Quat_{["x", "y", "z"][i]}_norm: {quat_data_normalized[-1, i]:.2f}')

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', force=True)
    p = multiprocessing.Process(target=worker, args=(q,))
    p.start()

    while q.empty():
        continue

    anim_imu = animation.FuncAnimation(fig_imu, animate, blit=False, interval=50, save_count=100)
    anim_quat = animation.FuncAnimation(fig_quat, animate, blit=False, interval=50, save_count=100)

    def on_close(event):
        p.terminate()
        raise KeyboardInterrupt
        print("On close has ran")

    fig_imu.canvas.mpl_connect('close_event', on_close)
    fig_quat.canvas.mpl_connect('close_event', on_close)

    try:
        plt.show()
    except KeyboardInterrupt:
        plt.close()
        p.close()
        quit()
