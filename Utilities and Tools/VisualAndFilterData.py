import pandas as pd
import matplotlib.pyplot as plt

# Cambia las rutas a las rutas locales donde tienes los archivos
data_quieto = pd.read_csv('myo_data_exp_quieto.txt', delimiter='\t')
data_movil = pd.read_csv('Myo_data_exp_movil.txt', delimiter='\t')

# Visualización de datos
def plot_data(data, title):
    plt.figure(figsize=(15, 10))
    plt.suptitle(title)
    
    plt.subplot(3, 1, 1)
    plt.plot(data['Timestamp'], data[['Acc_x', 'Acc_y', 'Acc_z']])
    plt.title('Aceleración')
    plt.xlabel('Timestamp')
    plt.ylabel('Aceleración')
    
    plt.subplot(3, 1, 2)
    plt.plot(data['Timestamp'], data[['Gyro_x', 'Gyro_y', 'Gyro_z']])
    plt.title('Giroscopio')
    plt.xlabel('Timestamp')
    plt.ylabel('Giroscopio')
    
    plt.subplot(3, 1, 3)
    plt.plot(data['Timestamp'], data[['Quat_w', 'Quat_x', 'Quat_y', 'Quat_z']])
    plt.title('Cuaterniones')
    plt.xlabel('Timestamp')
    plt.ylabel('Cuaterniones')
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

plot_data(data_quieto, 'Datos en Reposo')
plot_data(data_movil, 'Datos en Movimiento')

# Filtrado de datos (ejemplo simple usando media móvil)
data_quieto_filtered = data_quieto.rolling(window=5).mean()
data_movil_filtered = data_movil.rolling(window=5).mean()

plot_data(data_quieto_filtered, 'Datos en Reposo (Filtrados)')
plot_data(data_movil_filtered, 'Datos en Movimiento (Filtrados)')
