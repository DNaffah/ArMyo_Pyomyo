
import pygame          
from pygame.locals import *
from pynput.keyboard import Key, Controller
from pyomyo import Myo, emg_mode
from pyomyo.Classifier import Live_Classifier, MyoClassifier, EMGHandler
from xgboost import XGBClassifier
import Client 
import time

from sklearn.ensemble import RandomForestClassifier
# from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
# from sklearn.neural_network import MLPClassifier


host = '192.168.164.68'  # Dirección IP de tu Raspberry Pi
port = 12345  # Puerto en el que está escuchando tu servidor en la Raspberry Pi


def dino_handler(pose):
	print("Pose detected", pose)
	message = str(pose)
	#Client.enviar_datos(client_socket, message)
	time.sleep(0.7)
if __name__ == '__main__':
	keyboard = Controller()
	#client_socket = Client.conectar_a_servidor(host, port)  
    
	pygame.init()
	w, h = 800, 320
	scr = pygame.display.set_mode((w, h))
	font = pygame.font.Font(None, 30)

	## Modelo de escalas logaritmicas en funciones no lineales
	# model = XGBClassifier(eval_metric='logloss')
	# clr = Live_Classifier(model, name="XG", color=(255,0,150))
	
	
	## Modelo de Red Perceptor multientrada
	# model = MLPClassifier(hidden_layer_sizes=(80,30), max_iter=10000)
	# clr = Live_Classifier(model, name="MLP", color=(75, 92, 115))
	
	## Modelo de vectores (No funciona por motivos de dependencia y no calibracion in "LIVE")
	# model = SVC(kernel='rbf', C=1.0, gamma='scale') # Modelo para entrenar no "Live"
	# clr = Live_Classifier(model, name="SVM", color=(255, 0, 150))
	
	## Modelo De Vecinos (sin probar)
	#model = KNeighborsClassifier(n_neighbors=8)
	#clr = Live_Classifier(model, name="KNN", color=(255, 0, 150))
	## Modelo de arbol aleatorio 
	model = RandomForestClassifier(n_estimators=60, random_state=0)
	clr = Live_Classifier(model, name="RandomForest", color=(255, 0, 150))
	m = MyoClassifier(clr, mode=emg_mode.PREPROCESSED, hist_len=40)
	hnd = EMGHandler(m)
	m.add_emg_handler(hnd)

	m.connect()

	m.add_raw_pose_handler(dino_handler)

                                                                                                                                                                                    
	# Set Myo LED color to model color
	m.set_leds(m.cls.color, m.cls.color)
	# Set pygame window name
	pygame.display.set_caption(m.cls.name)
	
	try:
		while True:
			# Run the Myo, get more data
			m.run()
			# Run the classifier GUI
			m.run_gui(hnd, scr, font, w, h)			

	except KeyboardInterrupt:
		pass
	finally:
		m.disconnect()
		print()
		#client_socket.close()
		pygame.quit()