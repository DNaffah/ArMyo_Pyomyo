

import pygame          
from pygame.locals import *
from pynput.keyboard import Key, Controller
from pyomyo import Myo, emg_mode
from pyomyo.Classifier import Live_Classifier, MyoClassifier, EMGHandler
from xgboost import XGBClassifier

TRAINING_MODE = False

def dino_handler(pose):
	print("Pose detected", pose)
	if ((pose == 1) and (TRAINING_MODE == False)):
		for i in range(0,10):
			# Press and release space
			keyboard.press(Key.space)
			keyboard.release(Key.space)

if __name__ == '__main__':
	keyboard = Controller()

	pygame.init()
	w, h = 800, 320
	scr = pygame.display.set_mode((w, h))
	font = pygame.font.Font(None, 30)

	# Make an ML Model to train and test with live
	# XGBoost Classifier Example
	model = XGBClassifier(eval_metric='logloss')
	clr = Live_Classifier(model, name="XG", color=(178,255,77))
	m = MyoClassifier(clr, mode=emg_mode.PREPROCESSED, hist_len=10)

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
		pygame.quit()