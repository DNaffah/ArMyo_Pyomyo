import socket

def conectar_a_servidor(host, port):
    # Crea un socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Conecta el socket al servidor
    client_socket.connect((host, port))

    return client_socket

def enviar_datos(client_socket, message):
    # Envía los datos al servidor
    client_socket.send(message.encode('utf-8'))

# Ejemplo de uso:
#client_socket = conectar_a_servidor('192.168.1.41', 12345)
#while True:
#     message = input("Ingrese un mensaje ('exit' para salir): ")
#     enviar_datos(client_socket, message)
#     if message == 'exit':
#         break
#client_socket.close()