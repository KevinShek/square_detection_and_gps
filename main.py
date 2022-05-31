import time
import cv2
import csv
from pathlib import Path
import itertools
from config import Settings
from saving import Saving
from detection import detection

"""
The following code contains the detection of the square target and saves only the inner square data
"""

def GPS_calculation(config, positions, centres, headings, marker):
    # Get middle position within lists outputted by detection function
    middle = int(len(positions) / 2)
    image_dimensions = [config.width, config.height]
    targetCoords = locating_gps.GPS(centres[middle], headings[middle], positions[middle][0], positions[middle][1], positions[middle][2], image_dimensions) 
                
    print(f"{targetCoords[0]} latitude and {targetCoords[1]} longitude of {marker}")

    return targetCoords


def solution(counter, marker, targetCoords, result_dir):   
    # extracting the latitude and longitude of the GPS
    lat = targetCoords[0]
    long = targetCoords[1]

    with open(f'{result_dir}/results.csv', 'a') as csvfile:  # for testing purposes
        filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        filewriter.writerow([str(marker), str(lat), str(long)])

    print("Detection of Target", marker, "is saved")

    counter = 1

    return marker, counter


def capture_setting():
    # intialising the key information
    counter = 1
    marker = 1
    config = Settings()
    save = Saving(config.name_of_folder, config.exist_ok)
    targetCoords = [0,0,0]
    positions = [0, 0, 0]

    # Connecting to the Pixhawk and gathering data
    if config.GPS:
        import locating_gps
        print('Connecting to drone...')

        # Connect to vehicle and print some info
        vehicle = connect('192.168.0.156:14550', wait_ready=True, baud=921600)

        print('Connected to drone')
        print('Autopilot Firmware version: %s' % vehicle.version)
        print('Global Location: %s' % vehicle.location.global_relative_frame)


    if config.capture == "pc":
        if config.testing:
            cap = cv2.VideoCapture(config.media)
        else:
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)  # 800 default
            cap.set(3, config.width)  # 800 default
            cap.set(4, config.height)  # 800 default
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)
            cap.set(cv2.CAP_PROP_FPS, 60)

            time.sleep(2)  # allows the camera to start-up
        print('Camera on')
        while True:
            _, frame = cap.read()
            if config.Step_camera:
                cv2.imshow('frame', frame)
                k = cv2.waitKey(5) & 0xFF
                if k == 27:
                    break

            # grab the gps details
            if config.GPS:
                position = vehicle.location.global_relative_frame
                positions = [position.lat, position.lon, position.alt]
                heading = vehicle.heading

            # detecting the 2 square target and return the images and if it was successful or not
            color, roi, frame, centre_target, success = detection(frame, config)

            # storing the information onto a csv file
            solution(counter, marker, targetCoords, save.save_dir)

            if success:
                counter = counter + 1

                if config.save_results:
                    name_of_results = ["color", "roi", "frame"]
                    image_results = [color, roi, frame]
                    for value, data in enumerate(name_of_results):
                        image_name = f"{marker}_{data}_{counter}.jpg"
                        image = image_results[value]
                        if image is not None:
                            save.save_the_image(image_name, image)
                
                # storing the information onto a csv file
                solution(counter, marker, save.save_dir)
                marker = marker + 1


    elif config.capture == "pi":
        from picamera.array import PiRGBArray
        from picamera import PiCamera

        camera = PiCamera()
        camera.resolution = (config.width, config.height)
        camera.brightness = 50  # 50 is default
        camera.framerate = 90
        camera.awb_mode = 'auto'
        camera.shutter_speed = camera.exposure_speed
        cap = PiRGBArray(camera, size=(config.width, config.height))
        print('Camera on')

        for image in camera.capture_continuous(cap, format="bgr", use_video_port=True):
            #  to start the progress of capture and don't stop unless the counter increases and has surpass 5 seconds
            frame = image.array

            # grab the gps details
            if config.GPS:
                position = vehicle.location.global_relative_frame
                positions = [position.lat, position.lon, position.alt]
                heading = vehicle.heading

            # detecting the 2 square target and return the images and if it was successful or not
            color, roi, frame, centre_target, success = detection(frame, config)
            
            if success:
                counter = counter + 1

                if config.save_results:
                    name_of_results = ["color", "roi", "frame"]
                    image_results = [color, roi, frame]
                    for value, data in enumerate(name_of_results):
                        image_name = f"{marker}_{data}_{counter}.jpg"
                        image = image_results[value]
                        if image is not None:
                            save.save_the_image(image_name, image)
                
                if config.GPS:
                    targetCoords = GPS_calculation(config, positions, centre_target, heading, marker)

                # storing the information onto a csv file
                solution(counter, marker, targetCoords, save.save_dir)
                marker = marker + 1

            cap.truncate(0)
                
    elif config.capture == "image_folder":
        cap = [] # to store the names of the images
        detected = 0
        data_dir = Path(config.media)

        # the following code interite over the extension that exist within a folder and place them into a single list
        image_count = list(itertools.chain.from_iterable(data_dir.glob(pattern) for pattern in ('*.jpg', '*.png')))
        # image_count = len(list(data_dir.glob('*.jpg')))
        for name in image_count:
                # head, tail = ntpath.split(name)
                filename = Path(name)  # .stem removes the extension and .name grabs the filename with extension
                cap.append(filename)
                test_image = cv2.imread(str(filename))
                marker = Path(name).stem # grabs the name with the extension

                # detecting the 2 square target and return the images and if it was successful or not
                color, roi, frame, _, success = detection(test_image, config)
                
                if success:
                    counter = counter + 1
                    detected = detected + 1

                    if config.save_results:
                        name_of_results = ["color", "roi", "frame"]
                        image_results = [color, roi, frame]
                        for value, data in enumerate(name_of_results):
                            image_name = f"{marker}_{data}.jpg"
                            image = image_results[value]
                            if image is not None:
                                save.save_the_image(image_name, image)
                    
                    # storing the information onto a csv file
                    solution(counter, marker, targetCoords, save.save_dir)
        print(f"there is a total image count of {len(image_count)}, frames appended {len(cap)} and the total detection of the square target is {detected}.")


def main():
    print('Starting detection')
    capture_setting()


if __name__ == "__main__":
    main()
