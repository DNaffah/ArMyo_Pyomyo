import cv2
import csv
import time
import os
from pyomyo import Myo, emg_mode

class Listener:
    def __init__(self):
        self.myo = Myo(mode=emg_mode.PREPROCESSED)
        self.myo.connect()
        self.myo.add_imu_handler(self.proc_imu)
        self.myo.add_battery_handler(self.proc_battery)
        self.data = []
        self.start_time = time.time()
        
        # Video capture setup
        self.cap = cv2.VideoCapture(0)
        self.out = cv2.VideoWriter(f'video_{time.strftime("%Y%m%d_%H%M%S")}.avi',
                                   cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))

    def proc_imu(self, quat, acc, gyro):
        timestamp = time.time() - self.start_time
        self.data.append([timestamp, quat, acc, gyro])
        print(f"Timestamp: {timestamp:.2f}, Cuaternión: {quat}, Acelerómetro: {acc}, Giroscopio: {gyro}")

    def proc_battery(self, battery_level):
        print(f"Nivel de batería: {battery_level}")

    def run(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if ret:
                    # Convert frame to grayscale
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # Apply GaussianBlur to reduce image noise
                    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                    # Detect edges in the image
                    edged = cv2.Canny(blurred, 50, 150)

                    # Find contours in the edged image
                    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    for contour in contours:
                        # Approximate the contour
                        peri = cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                        # If the contour has a significant area and a shape that resembles the Myo armband
                        if len(approx) > 5 and cv2.contourArea(contour) > 500:
                            x, y, w, h = cv2.boundingRect(approx)
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Display the resulting frame
                    self.out.write(frame)
                    cv2.imshow('frame', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                self.myo.run()
                time.sleep(0.01)
        except KeyboardInterrupt:
            print("Desconectando...")
        finally:
            self.myo.disconnect()
            self.cap.release()
            self.out.release()
            cv2.destroyAllWindows()
            with open(f'data_{time.strftime("%Y%m%d_%H%M%S")}.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Quaternion', 'Accelerometer', 'Gyroscope'])
                writer.writerows(self.data)

if __name__ == '__main__':
    listener = Listener()
    listener.run()
