import os
import cv2
import numpy as np


class Settings:
    def __init__(self):
        # The steps of the programs
        self.Step_camera = False  # stages of camera activating
        self.Step_detection = False  # stages of detection

        # Saving the data depending on the situation, only one of the 3 settings can be set true at a time
        self.save_results = True  # to allow saving to occur
        self.name_of_folder = "exp" # name of the folder that could be found in "result_dir/exp"
        self.exist_ok = False # it would save the content into the same name of folder if it exist within result_dir

        # Provide a video or dataset you wish to test against
        self.media = "test_images"  # video used for testing and has to be in the exact location of the config file
        # video/target_only.mp4

        # Information
        self.capture = "pi"  # where are the frames coming from? (pc/pi/image_folder) 
        self.GPS = False # do you want the GPS code to be working? (True/False)

        # Camera setting
        self.camera_angle = 62.2 # the camera angle of the raspberry pi camera v2
        self.width = 1280
        self.height = 720

        # video
        self.testing = False  # are you running a test on the PC with a video? (True/False)

        # Testing the recognition to enable this capture has to be "image" and testing = "character" or "colour",
        # one at a time.
        self.character_test = False  # character recognition test
        self.colour_test = False  # colour recognition test
