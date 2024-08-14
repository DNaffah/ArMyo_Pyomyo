import os
from pyomyo import Myo, emg_mode
import time
import csv
from ArMyo_Pyomyo.src.pyomyo.pyomyo import cls

class Listener:
    def __init__(self):
        self.myo = Myo(mode=emg_mode.PREPROCESSED)
        self.myo.connect()
        self.myo.add_imu_handler(self.proc_imu)
        self.myo.add_battery_handler(self.proc_battery)

        # Crear o abrir archivo CSV
        self.csv_file = open('myo_data_movil.csv', mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Timestamp', 'Quat_w', 'Quat_x', 'Quat_y', 'Quat_z', 
                                  'Acc_x', 'Acc_y', 'Acc_z', 'Gyro_x', 'Gyro_y', 'Gyro_z'])
        self.timestamp = 0.0

    def proc_imu(self, quat, acc, gyro):
        quat_w, quat_x, quat_y, quat_z = quat
        acc_x, acc_y, acc_z = acc
        gyro_x, gyro_y, gyro_z = gyro
        
        # Escribir datos en el archivo CSV
        self.csv_writer.writerow([self.timestamp, quat_w, quat_x, quat_y, quat_z, 
                                  acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z])
        self.timestamp += 0.01

    def proc_battery(self, battery_level):
        print(f"Nivel de batería: {battery_level}")

    def run(self):
        try:
            while True:
                cls()
                self.myo.run()
                time.sleep(0.01)
        except KeyboardInterrupt:
            print("Desconectando...")
            self.myo.disconnect()
            self.csv_file.close()

if __name__ == '__main__':
    listener = Listener()
    listener.run()
