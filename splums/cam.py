import cv2
import os
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage


#Threaded camworker, to run in parallel with main GUI program
class CamWorker(QThread):
    
    #Signal to update the image in GUI
    image_update = pyqtSignal(QImage)

    def __init__(self, name):
        #Name of student
        self.name = name
        super(QThread, self).__init__()

    #AUTOMATICALLY RUNS when you call the built in start() command on this thread
    def run(self):
        self.file_name = self.name.replace(" ", "_")
        # Get default video gamera
        camera = cv2.VideoCapture(0)

        #Thread is being ran, unsure if this is needed, but it works so I wouldn't tamper with it.
        self.thread_active = True

        #Used to determine whether or not to continiously update feed
        self.pic_taken = False

        while self.thread_active:
            ret, self.frame = camera.read()
            # Video if a picture has not yet been taken, and the webcam is currently returning frames
            if not self.pic_taken and ret:
                #Converting the frame to an image, and formatting it properly
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

                #Flip the image, this will make the webcam act as a mirror, making it feel more natural to line your face with the camera
                flipped_image = cv2.flip(image, 1)
                qt_formatted_image = QImage(flipped_image.data, flipped_image.shape[1], flipped_image.shape[0], QImage.Format.Format_RGB888)

                #This is where the image is scaled, this resolution is the resolution the images are saved in, might be slightly different, depending on aspect ratio.
                pic = qt_formatted_image.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)

                #Emitting of the signal to update the video feed in GUI
                self.image_update.emit(pic)

        #turn off camera after the loop is over
        camera.release()


    def take_picture(self):
        #stops video feed
        self.pic_taken = True

        # check to add dir
        if not os.path.exists("./images/"):
            os.makedirs("./images/")
        
        #saves to [PATH THIS PROGRAM IS RAN]/images
        file_path = "./images/" + self.file_name + ".jpg"
        cv2.imwrite(file_path, self.frame)

    def retake_picture(self):
        #Resumes video feed
        self.pic_taken = False

    #What to do when closing
    def stop(self):
        #Stop thread and exit
        self.thread_active = False
        self.quit()
