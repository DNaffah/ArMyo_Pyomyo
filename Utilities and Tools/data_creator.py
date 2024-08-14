import os

# Directorio donde se almacenarán los archivos
directory = 'data'

# Verificar si el directorio existe, si no, crearlo
if not os.path.exists(directory):
    os.makedirs(directory)

open('data/vals0.dat', 'wb').close()
open('data/vals1.dat', 'wb').close()
open('data/vals2.dat', 'wb').close()
open('data/vals3.dat', 'wb').close()
open('data/vals4.dat', 'wb').close()
open('data/vals5.dat', 'wb').close()
open('data/vals6.dat', 'wb').close()
open('data/vals7.dat', 'wb').close()
open('data/vals8.dat', 'wb').close()
open('data/vals9.dat', 'wb').close()