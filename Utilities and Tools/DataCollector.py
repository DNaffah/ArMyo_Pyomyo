import os
from pyomyo import Myo, emg_mode
import time
import pandas as pd
from datetime import datetime
from ArMyo_Pyomyo.src.pyomyo.pyomyo import cls

class Listener:
    def __init__(self):
        self.myo = Myo(mode=emg_mode.PREPROCESSED)
        self.myo.connect()
        self.myo.add_imu_handler(self.proc_imu)
        # Se omite la función proc_emg ya que no es necesaria para este experimento
        self.myo.add_battery_handler(self.proc_battery)
        self.data = {
            'Timestamp': [],
            'Quat_w': [], 'Quat_x': [], 'Quat_y': [], 'Quat_z': [],
            'Acc_x': [], 'Acc_y': [], 'Acc_z': [],
            'Gyro_x': [], 'Gyro_y': [], 'Gyro_z': []
        }

    def proc_imu(self, quat, acc, gyro):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.data['Timestamp'].append(timestamp)
        self.data['Quat_w'].append(quat[0])
        self.data['Quat_x'].append(quat[1])
        self.data['Quat_y'].append(quat[2])
        self.data['Quat_z'].append(quat[3])
        self.data['Acc_x'].append(acc[0])
        self.data['Acc_y'].append(acc[1])
        self.data['Acc_z'].append(acc[2])
        self.data['Gyro_x'].append(gyro[0])
        self.data['Gyro_y'].append(gyro[1])
        self.data['Gyro_z'].append(gyro[2])
        print(f"Cuaternión: {quat}")
        print(f"Acelerómetro: {acc}")
        print(f"Giroscopio: {gyro}")

    def proc_battery(self, battery_level):
        print(f"Nivel de batería: {battery_level}")

    def save_data(self):
        df = pd.DataFrame(self.data)
        df.to_excel('imu_data.xlsx', index=False)
        print("Datos guardados en imu_data.xlsx")

    def run(self):
        try:
            while True:
                cls()
                self.myo.run()
                time.sleep(0.01)
        except KeyboardInterrupt:
            print("Desconectando...")
            self.save_data()
            self.myo.disconnect()

if __name__ == '__main__':
    listener = Listener()
    listener.run()
