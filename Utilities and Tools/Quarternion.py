import numpy as np

def normalize_quaternion(q):
    """
    Normaliza un cuaternión para que tenga una magnitud de 1.
    """
    norm = np.linalg.norm(q)
    if norm == 0:
        raise ValueError("La magnitud del cuaternión es cero, no se puede normalizar.")
    return q / norm

def quaternion_to_rotation_matrix(q):
    """
    Convierte un cuaternión normalizado a una matriz de rotación.
    q = [w, x, y, z]
    """
    w, x, y, z = q
    return np.array([
        [1 - 2*y**2 - 2*z**2, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
        [2*x*y + 2*z*w, 1 - 2*x**2 - 2*z**2, 2*y*z - 2*x*w],
        [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x**2 - 2*y**2]
    ])

def apply_rotation(point, rotation_matrix):
    """
    Aplica una matriz de rotación a un punto.
    """
    return np.dot(rotation_matrix, point)

# Ejemplo de uso
quaternion = np.array([0.7071, 0.0, 0.7071, 0.0])  # Ejemplo de cuaternión
initial_point = np.array([1, 0, 0])  # Punto inicial en el espacio

# Normalizar el cuaternión
normalized_quaternion = normalize_quaternion(quaternion)

# Convertir cuaternión a matriz de rotación
rotation_matrix = quaternion_to_rotation_matrix(normalized_quaternion)

# Aplicar la rotación al punto
new_point = apply_rotation(initial_point, rotation_matrix)

print("Punto inicial:", initial_point)
print("Nuevo punto después de la rotación:", new_point)
print("Cuaternión normalizado:", normalized_quaternion)
print("Magnitud del cuaternión normalizado:", np.linalg.norm(normalized_quaternion))
