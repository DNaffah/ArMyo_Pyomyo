import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore
import numpy as np
from sklearn.model_selection import train_test_split
from PIL import Image
import matplotlib.pyplot as plt

# Configuración del generador de datos
datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

# Cargar imágenes
image_dir = 'data_img'
image_paths = [os.path.join(image_dir, fname) for fname in os.listdir(image_dir)]
images = [Image.open(path).resize((150, 150)) for path in image_paths]
images = np.array([np.array(img) for img in images])

# Crear etiquetas (1 para imágenes con brazalete, 0 para sin brazalete)
labels = np.array([1 if 'bracelet' in fname else 0 for fname in os.listdir(image_dir)])

# Dividir en conjunto de entrenamiento y validación
X_train, X_val, y_train, y_val = train_test_split(images, labels, test_size=0.2, random_state=42)

# Generador de datos de entrenamiento
train_gen = datagen.flow(X_train, y_train, batch_size=16)

# Generador de datos de validación
val_gen = datagen.flow(X_val, y_val, batch_size=16)

# Definición del modelo
model = tf.keras.models.Sequential([
    tf.keras.layers.Input(shape=(150, 150, 3)),
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# Compilación del modelo
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Ajuste de los parámetros de steps_per_epoch y validation_steps
steps_per_epoch = len(X_train) // 16
validation_steps = len(X_val) // 16

# Configuración de TensorFlow para reducir el uso de memoria
physical_devices = tf.config.list_physical_devices('GPU')
if len(physical_devices) > 0:
    for device in physical_devices:
        tf.config.experimental.set_memory_growth(device, True)

# Entrenamiento del modelo
history = model.fit(
    train_gen,
    steps_per_epoch=steps_per_epoch,
    validation_data=val_gen,
    validation_steps=validation_steps,
    epochs=10
)

# Guardar el modelo entrenado
model.save('bracelet_detector_model.h5')

# Graficar los resultados del entrenamiento
plt.plot(history.history['accuracy'], label='Accuracy')
plt.plot(history.history['val_accuracy'], label='Val Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.ylim([0, 1])
plt.legend(loc='lower right')
plt.show()
