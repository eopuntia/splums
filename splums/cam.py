import cv2
import os
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage

#Threaded camworker, to run in parallel with main GUI program
class CamWorker(QThread):
    #Signal to update the image in GUI
    image_update = pyqtSignal(QImage)

    def __init__(self, win):
        super(QThread, self).__init__()
        #Name of student
        self.file_name = win

    #AUTOMATICALLY RUNS when you call the built in start() command on this thread
    def run(self):
        # Get default video gamera
        camera = cv2.VideoCapture(0)

        self.thread_active = True

        #Used to determine whether or not to continiously update feed
        self.pic_taken = False

        while self.thread_active:
            if self.pic_taken == False:
                ret, self.frame = camera.read()
            # Video if a picture has not yet been taken, and the webcam is currently returning frames
            if not self.pic_taken and ret:
                #Converting the frame to an image, and formatting it properly
                # flip the image
                image = cv2.flip(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB), 1)

                qt_formatted_image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format.Format_RGB888)

                #This is where the image is scaled, this resolution is the resolution the images are saved in, might be slightly different, depending on aspect ratio.
                pic = qt_formatted_image.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)

                #Emitting of the signal to update the video feed in GUI
                self.image_update.emit(pic)

        #turn off camera after the loop is over
        camera.release()

    def take_picture(self):
        #stops video feed
        self.pic_taken = True

    def save_photo(self):
        # check to add dir
        if not os.path.exists("./images/"):
            os.makedirs("./images/")
        
        #saves to [PATH THIS PROGRAM IS RAN]/images
        file_path = "./images/" + self.file_name + ".jpg"
        cv2.imwrite(file_path, self.frame)

        self.pic_taken = False

    def retake_picture(self):
        #Resumes video feed
        self.pic_taken = False

    #What to do when closing
    def stop(self):
        #Stop thread and exit
        self.thread_active = False
        self.quit()
