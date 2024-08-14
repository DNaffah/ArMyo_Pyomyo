import time
import numpy as np
from pyomyo import Myo, emg_mode

class IMU:
    def __init__(self):
        self.prev_quaternion = None

    def normalize_quaternion(self, q):
        norm = np.linalg.norm(q)
        if norm == 0:
            raise ValueError("La magnitud del cuaternión es cero, no se puede normalizar.")
        return q / norm

    def analyze_quaternion(self, quaternion):
        normalized_quaternion = self.normalize_quaternion(quaternion)
        if self.prev_quaternion is not None:
            delta = np.abs(normalized_quaternion - self.prev_quaternion)
            print("Delta:", delta)
        self.prev_quaternion = normalized_quaternion
        print("Cuaternión Normalizado:", normalized_quaternion)
        w, x, y, z = normalized_quaternion
        print(f"w: {w}, x: {x}, y: {y}, z: {z}")

# Función de callback para imprimir y analizar los datos del IMU
def imu_callback(quaternion, accel, gyro):
    imu.analyze_quaternion(quaternion)
    print("Acelerómetro:", accel)
    print("Giroscopio:", gyro)
    print("------------")

# Crear una instancia del Myo
myo = Myo(mode=emg_mode.PREPROCESSED)
myo.connect()

# Crear una instancia de la clase IMU
imu = IMU()

# Asignar la función de callback para los datos IMU
myo.add_imu_handler(imu_callback)

# Iniciar la recepción de datos del Myo
try:
    while True:
        myo.run()
        time.sleep(0.5)  # Tomar datos cada medio segundo
except KeyboardInterrupt:
    myo.disconnect()
    print("Desconectado del Myo")
