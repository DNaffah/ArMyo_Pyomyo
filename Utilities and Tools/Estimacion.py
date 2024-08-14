import os
import time
import numpy as np
from pyomyo import Myo, emg_mode
def cls():
	# Clear the screen in a cross platform way
	# https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console
    os.system('cls' if os.name=='nt' else 'clear')

class IMU:
    def __init__(self, dt=0.01):
        self.gyro_bias = np.zeros(3)
        self.dt = dt  # Intervalo de tiempo entre mediciones (en segundos)
        self.orientation = np.array([1.0, 0.0, 0.0, 0.0])  # Cuaternión unitario inicial
        self.position = np.zeros(3)
        self.velocity = np.zeros(3)

    def normalize_quaternion(self, q):
        norm = np.linalg.norm(q)
        if norm == 0:
            raise ValueError("La magnitud del cuaternión es cero, no se puede normalizar.")
        return q / norm

    def quaternion_to_rotation_matrix(self, q):
        w, x, y, z = q
        return np.array([
            [1 - 2*y**2 - 2*z**2, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
            [2*x*y + 2*z*w, 1 - 2*x**2 - 2*z**2, 2*y*z - 2*x*w],
            [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x**2 - 2*y**2]
        ])

    def quaternion_multiply(self, q1, q2):
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        w = w1*w2 - x1*x2 - y1*y2 - z1*z2
        x = w1*x2 + x1*w2 + y1*z2 - z1*y2
        y = w1*y2 - x1*z2 + y1*w2 + z1*x2
        z = w1*z2 + x1*y2 - y1*x2 + z1*w2
        return np.array([w, x, y, z])

    def integrate_gyroscope(self, gyro_data):
        w, x, y, z = self.orientation
        gx, gy, gz = gyro_data - self.gyro_bias

        # Convertir velocidades angulares a radianes por segundo
        gx, gy, gz = np.radians([gx, gy, gz])

        # Integración simple de las velocidades angulares para actualizar la orientación
        delta_quaternion = np.array([0, gx, gy, gz]) * self.dt * 0.5
        delta_quaternion = np.concatenate(([1], delta_quaternion))  # w = 1 para la integración
        self.orientation = self.quaternion_multiply(self.orientation, delta_quaternion)
        self.orientation = self.normalize_quaternion(self.orientation)

    def update_position(self, accel_data):
        # Convertir aceleración del sistema de coordenadas del dispositivo al global
        rotation_matrix = self.quaternion_to_rotation_matrix(self.orientation)
        accel_global = np.dot(rotation_matrix, accel_data)
        
        # Restar la gravedad
        accel_global[2] -= 9.81

        # Integrar la aceleración para obtener la velocidad y luego la posición
        self.velocity += accel_global * self.dt
        self.position += self.velocity * self.dt

    def update(self, gyro_data, accel_data, quaternion):
        self.orientation = self.normalize_quaternion(quaternion)  # Actualizar orientación directamente con el cuaternión
        self.update_position(accel_data)

# Función de callback para actualizar los datos del IMU
def imu_callback(quaternion, accel, gyro):
    imu.update(gyro, accel, quaternion)
    print("Orientación (cuaternión):", imu.orientation)
    print("Posición estimada:", imu.position)

# Crear una instancia de la clase IMU
imu = IMU(dt=0.01)

# Configurar el brazalete Myo
myo = Myo(mode=emg_mode.PREPROCESSED)
myo.connect()

# Asignar la función de callback para los datos IMU
myo.add_imu_handler(imu_callback)

# Iniciar la recepción de datos del Myo
try:
    while True:
        myo.run()
        time.sleep(imu.dt)
        cls()
except KeyboardInterrupt:
    myo.disconnect()
    print("Desconectado del Myo")
