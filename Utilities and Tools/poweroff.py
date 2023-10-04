import time
from pyomyo import Myo, emg_mode
# Make a Myo object
m = Myo(mode=emg_mode.RAW)
# Connect to it
m.connect()
print("Turning the Myo off.")
print("Charge it to reboot it.")
print("Press Ctrl + Break.")
m.vibrate(1)
# Wait until it vibrates before turning it off
time.sleep(2)
# Turn it off
m.power_off()
quit()