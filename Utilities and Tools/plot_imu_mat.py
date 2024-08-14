import multiprocessing
import queue
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
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
# Set the size of the plot
plt.rcParams["figure.figsize"] = (10, 12)
fig, subplots = plt.subplots(3, 1, figsize=(10, 8))
fig.canvas.manager.set_window_title("IMU Data Plot")
fig.tight_layout()

# Initialize lines
acc_lines = [subplots[0].plot(range(QUEUE_SIZE), [0] * QUEUE_SIZE, label=axis)[0] for axis in ['Acc_x', 'Acc_y', 'Acc_z']]
gyro_lines = [subplots[1].plot(range(QUEUE_SIZE), [0] * QUEUE_SIZE, label=axis)[0] for axis in ['Gyro_x', 'Gyro_y', 'Gyro_z']]
quat_lines = [subplots[2].plot(range(QUEUE_SIZE), [0] * QUEUE_SIZE, label=axis)[0] for axis in ['Quat_w', 'Quat_x', 'Quat_y', 'Quat_z']]

for ax in subplots:
    ax.legend()

imu_queue = queue.Queue(QUEUE_SIZE)

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

        # Update lines
        for i, line in enumerate(acc_lines):
            line.set_ydata(acc_data[:, i])
            subplots[0].relim()
            subplots[0].autoscale_view()

        for i, line in enumerate(gyro_lines):
            line.set_ydata(gyro_data[:, i])
            subplots[1].relim()
            subplots[1].autoscale_view()

        for i, line in enumerate(quat_lines):
            line.set_ydata(quat_data[:, i])
            subplots[2].relim()
            subplots[2].autoscale_view()

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
