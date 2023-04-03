# Modified by Miguel Ribeiro, FlowMe.online for:
#   server send every minute
#   managing backups when network is unavailable, checking files integrity
#      send data when network is available again
#   allow camera to be disconnected and reconnected whitout crashing or restarting the service
#   confidence filter and display on frame,
#   log outputs on CSV files, 
#   Actual detection on the line, not just direction (as the original was), by tracking IDs, and managing centroids
#   Adding parameters to the detection line


# USAGE
# To read and write back out to video:
# python people_counter.py --prototxt mobilenet_ssd/MobileNetSSD_deploy.prototxt \
#   --model mobilenet_ssd/MobileNetSSD_deploy.caffemodel --input videos/example_01.mp4 \
#   --output output/output_01.avi
#
# To read from webcam and write back out to disk:
# python people_counter.py --prototxt mobilenet_ssd/MobileNetSSD_deploy.prototxt \
#   --model mobilenet_ssd/MobileNetSSD_deploy.caffemodel \
#   --output output/webcam_output.avi

from config import Config
from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
from imutils.video import VideoStream
from imutils.video import FPS
from pathlib import Path
import numpy as np
import argparse
import datetime
import imutils
import math
import time
import dlib
import cv2
import util

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
    help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
    help="path to Caffe pre-trained model")
ap.add_argument("-i", "--input", type=str,
    help="path to optional input video file")
ap.add_argument("-o", "--output", type=str,
    help="path to optional output video file")
ap.add_argument("-c", "--confidence", type=float, default=0.4,
    help="minimum probability to filter weak detections")
ap.add_argument("-dl", "--detection-line", type=float, default=0.5,
    help="detection line height in percentage (default: 0.5)")
ap.add_argument("-s", "--skip-frames", type=int, default=30,
    help="# of skip frames between detections")
ap.add_argument("-cam", "--camera", type=int, default=0,
    help="# of webcam list index to choose default 0")
ap.add_argument("-fw", "--framewidth", type=int, default=500,
    help="frame width to resize image (smaller is faster)")
ap.add_argument("-so", "--show-other", type=int, default=0,
    help="show other objects beside persons (doesn't count, only renders)")
ap.add_argument("-hd", "--hd-output", type=int, default=1,
    help="outputs the image in the same size as input, otherwise, exports with the resize frame width")
ap.add_argument("-ss", "--server-send", type=int, default=1,
    help="send data to remote server")
ap.add_argument("-gf", "--global-file", type=str, default='global_log',
    help="path to optional global file output")
args = vars(ap.parse_args())

start_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
print('')
print("[INFO] Start Datetime", start_datetime)

# define detection line height
detection_line = 1 / args["detection_line"]
print('[INFO] Detection line at', args["detection_line"], '% of screen. Height division =', detection_line)
print('')
print('[CMD ARGS] ----------------------')
for item in args:
    print(item + ':' + str(args[item]))
print('')
print('[CONFIG] ------------------------')

# init config
PATH_OUTPUT = 'output/'
PATH_OUTPUT_RUNS = PATH_OUTPUT + 'runs/'
GLOBAL_FILE_OUTPUT = args["global_file"] + ".csv"
CONFIG_FILENAME = "config_project.json"
CONFIG = Config()
CONFIG.load_config_values(CONFIG_FILENAME)
print('')


Path(PATH_OUTPUT_RUNS).mkdir(parents=True, exist_ok=True)


del_f = ";"
del_p = '\t'
headers = "id" + del_f + "date" + del_f + "time" + del_f +"down" + del_f +"up" + del_f +"type" + del_f + "movement" + del_f +"conf" + del_f +"total_down" + del_f +"total_up\n"
headers_print = headers.replace('\n', '').replace('date', 'date\t').replace('time', 'time\t').replace('total_down', 't_down').replace(del_f, del_p)

with open(PATH_OUTPUT_RUNS + "log_" + start_datetime + ".csv", "w") as f:
    f.write(headers)

TEXT_ID_COLOR 		= (96, 163, 39)
CIRCLE_COLOR		= TEXT_ID_COLOR
TEXT_STATUS_COLOR 	= (0, 84, 211)
TEXT_FPS_COLOR		= TEXT_STATUS_COLOR
RECT_COLOR			= (113, 204, 46)
LINE_DETECTOR_COLOR = (18, 156, 243)
RECT_NON_PERSON_COLOR = (185,128,41)


CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"]

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

if not args.get("input", False):
    print("[INFO] starting video stream...")
    devIndex = args.get("camera", False)
    vs = VideoStream(src=devIndex).start()
    time.sleep(2.0)
else:
    print("[INFO] opening video file...")
    vs = cv2.VideoCapture(args["input"])

writer = None

orig_W = None
orig_H = None
W = None
H = None

ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
trackers = []
confidence_arr = []
trackableObjects = {}
lastCentroid = {}

startTime = time.time()
fps_print = ""
FPSUpdateInterval = 100
totalFrames = 0
partialFrames = 0
totalDown = 0
totalUp = 0

fps = FPS().start()

send_to_server_buffer = []
last_server_send = time.time()

# loop over frames from the video stream
while True:
    orig_frame = vs.read()
    orig_frame = orig_frame[1] if args.get("input", False) else orig_frame

    if args["input"] is not None and orig_frame is None:
        break

    if orig_frame is None:
        print("[INFO] camera disconnected, attempting restart reading...")
        vs.stop()
        devIndex = args.get("camera", False)
        vs = VideoStream(src=devIndex).start()
        time.sleep(2.0)
        continue

    frame = imutils.resize(orig_frame, width=args.get("framewidth", False))
    if args['hd_output'] == 0:
    	orig_frame = frame
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    if orig_W is None or orig_H is None:
        (orig_H, orig_W) = orig_frame.shape[:2]
    if W is None or H is None:
        (H, W) = frame.shape[:2]

    if args["output"] is not None and writer is None:
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        writer = cv2.VideoWriter(args["output"], fourcc, 30,
            (orig_W, orig_H), True)

    status = "Waiting"
    rects = []

    if totalFrames % args["skip_frames"] == 0:
        status = "Detecting"
        trackers = []

        # convert the frame to a blob and pass the blob through the network and obtain the detections
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
        net.setInput(blob)
        detections = net.forward()

        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability)
            confidence = detections[0, 0, i, 2]
            if confidence >= args["confidence"]:
                idx = int(detections[0, 0, i, 1])

                # if the class label is not a person, ignore it
                if CLASSES[idx] != "person":
                	if args["show_other"] != 0:
	                    box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
	                    (startX, startY, endX, endY) = box.astype("int")
	                    cv2.rectangle(orig_frame, (int(round(startX * (orig_W / W ))), int(round(startY * (orig_H / H)))), (int(round(endX * (orig_W / W))), int(round(endY * (orig_H / H)))), RECT_NON_PERSON_COLOR , 1)
	                    centerX = endX - startX
	                    centerY = endY - startY
	                    cv2.putText(orig_frame, CLASSES[idx], (int(round(centerX * (orig_W / W))) - 10, int(round(centerY * (orig_H / H))) - 10), cv2.FONT_HERSHEY_DUPLEX , 1, RECT_NON_PERSON_COLOR, 1)
	                continue

                # compute the (x, y)-coordinates of the bounding box
                # for the object
                box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                (startX, startY, endX, endY) = box.astype("int")
                
                # construct a dlib rectangle object from the bounding
                # box coordinates and then start the dlib correlation
                # tracker
                tracker = dlib.correlation_tracker()
                rect = dlib.rectangle(startX.item(), startY.item(), endX.item(), endY.item())
                tracker.start_track(rgb, rect)

                trackers.append(tracker)
                confidence_arr.append(confidence)

    # otherwise, we should utilize our object *trackers* rather than
    # object *detectors* to obtain a higher frame processing throughput
    else:
        for tracker in trackers:
            status = "Tracking"

            # update the tracker and grab the updated position
            tracker.update(rgb)
            pos = tracker.get_position()

            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())
            rects.append((startX, startY, endX, endY))

    # draw a horizontal line in the center of the frame -- once an
    cv2.line(orig_frame, (0, math.floor(orig_H // detection_line)), (orig_W, math.floor(orig_H // detection_line)), LINE_DETECTOR_COLOR, 2)

    #draw rectangles around tracked objects
    for rect in rects:
    	cv2.rectangle(orig_frame, (round(rect[0] * (orig_W / W )), round(rect[1] * (orig_H / H))), (round(rect[2] * (orig_W / W)), round(rect[3] * (orig_H / H))), RECT_COLOR , 1)

    # use the centroid tracker to associate the (1) old object
    # centroids with (2) the newly computed object centroids
    objects = ct.update(rects)

    objects_i = len(confidence_arr) - len(objects.items()) # get the last items inserted in the confidence array
    for (objectID, centroid) in objects.items():
        to = trackableObjects.get(objectID, None)

        # if there is no existing trackable object, create one
        if to is None:
            to = TrackableObject(objectID, centroid)
            lastCentroid[objectID] = centroid[1]
        else:
            # the difference between the y-coordinate of the *current*
            # centroid and the mean of *previous* centroids will tell
            # us in which direction the object is moving (negative for
            # 'up' and positive for 'down')
            y = [c[1] for c in to.centroids]
            direction = centroid[1] - np.mean(y)
            to.centroids.append(centroid)

            if not to.counted:
                # if the direction is positive (moving up
                # ) AND the centroid is above the center line, count the object
                if direction < 0 and centroid[1] < math.floor(H // detection_line) and lastCentroid[objectID] >= math.floor(H // detection_line):
                    totalUp += 1
                    to.counted = True

                    send_to_server_buffer.append({
                        "loc_id": CONFIG.LOCATION_ID,
                        "dt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "epoch": round(time.time()),
                        "dir": 1,
                        "conf": round(float(confidence_arr[objects_i]), 2)
                    })

                    fileLine = (str(objectID)
                                + del_f + datetime.datetime.now().strftime("%Y-%m-%d")
                                + del_f + datetime.datetime.now().strftime("%H:%M:%S")
                                + del_f + "0"
                                + del_f + "1"
                                + del_f + "1"
                                + del_f + "pos"
                                + del_f + str(round(float(confidence_arr[objects_i]), 2))
                                + del_f + str(totalDown)
                                + del_f + str(totalUp) + "\n")
                    with open(PATH_OUTPUT_RUNS + "log_" + start_datetime + ".csv", "a") as f:
                        f.write(fileLine)
                    with open(PATH_OUTPUT + GLOBAL_FILE_OUTPUT, "a") as f:
                        f.write(fileLine)
                    printLine = fileLine.replace('\n', '').replace(del_f, del_p)
                    if objectID % 10 == 0:
                        print(headers_print)
                    print(printLine)

                # if the direction is negative (moving down
                # ) AND the centroid is below the center line, count the object
                elif direction > 0 and centroid[1] > math.floor(H // detection_line) and lastCentroid[objectID] <= math.floor(H // detection_line):
                    totalDown += 1
                    to.counted = True

                    send_to_server_buffer.append({
                        "loc_id": CONFIG.LOCATION_ID,
                        "dt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "epoch": round(time.time()),
                        "dir": -1,
                        "conf": round(float(confidence_arr[objects_i]), 2)
                    })
                    
                    fileLine = (str(objectID)
                                + del_f + datetime.datetime.now().strftime("%Y-%m-%d")
                                + del_f + datetime.datetime.now().strftime("%H:%M:%S")
                                + del_f + "1"
                                + del_f + "0"
                                + del_f + "-1"
                                + del_f + "neg"
                                + del_f + str(round(float(confidence_arr[objects_i]), 2))
                                + del_f + str(totalDown)
                                + del_f + str(totalUp) + "\n")
                    with open(PATH_OUTPUT_RUNS + "/log_" + start_datetime + ".csv", "a") as f:
                        f.write(fileLine)
                    with open(PATH_OUTPUT + "global_log.csv", "a") as f:
                        f.write(fileLine)
                    printLine = fileLine.replace('\n', '').replace(del_f, del_p)
                    if objectID % 10 == 0:
                        print(headers_print)
                    print(printLine)

        # store the trackable object in our dictionary
        trackableObjects[objectID] = to
        
        # clear dictionary based on the objectID, delete the 20th item ago if it exists
        if trackableObjects.get(objectID - 20, None) != None:
        	del trackableObjects[objectID - 20]
        # clear dictionary
        if lastCentroid.get(objectID - 20) != None:
        	del lastCentroid[objectID - 20]

        # draw both the ID of the object and the centroid on frame output
        text = "P {} | {}%".format(objectID, str(int(round(float(confidence_arr[objects_i]) * 100, 2))))
        cv2.putText(orig_frame, text, (int(round(centroid[0] * (orig_W / W))) - 10, int(round(centroid[1] * (orig_H / H))) - 10),
            cv2.FONT_HERSHEY_DUPLEX , 0.5, TEXT_ID_COLOR, 2)
        cv2.circle(orig_frame, (int(round(centroid[0] * (orig_W / W))), int(round(centroid[1] * (orig_H / H)))), 4, CIRCLE_COLOR, -1)
        objects_i += 1

    info = [
        ("Up", totalUp),
        ("Down", totalDown),
        ("Status", status),
    ]

    for (i, (k, v)) in enumerate(info):
        text = "{}: {}".format(k, v)
        cv2.putText(orig_frame, text, (10, orig_H - ((i * 20) + 16)),
            cv2.FONT_HERSHEY_DUPLEX , 0.7, TEXT_STATUS_COLOR, 2)

    if partialFrames >= FPSUpdateInterval:
        fps_print = str(round(partialFrames / (time.time() - startTime)))
        startTime = time.time()

    cv2.putText(orig_frame, fps_print, (orig_W - 35, 20),
            cv2.FONT_HERSHEY_DUPLEX , 0.7, TEXT_FPS_COLOR, 2)

    # cv2.putText(orig_frame, "flowme.online", (orig_W - 140, orig_H - 10),
            # cv2.FONT_HERSHEY_DUPLEX , 0.6, (180,175,80), 2)
    
    if writer is not None:
        writer.write(orig_frame)

    # cv2.imshow("Frame", orig_frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q") or key == 27:
        break

    totalFrames += 1
    partialFrames = partialFrames + 1 if partialFrames < FPSUpdateInterval else 0

    # send data to server
    if args["server_send"] == 1:
        if last_server_send + CONFIG.SEND_INTERVAL < time.time():
            print('-------------------')
            print('trying to upload data with ', len(send_to_server_buffer), ' records')
            # try to send, even if it has zero values, because it may have pending values in backup
            util.manage_upload_data(CONFIG, send_to_server_buffer)
            send_to_server_buffer = []
            last_server_send = time.time()
            print('-------------------')

# stop the timer and display FPS information
fps.stop()
#print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# check to see if we need to release the video writer pointer
if writer is not None:
    writer.release()

if not args.get("input", False):
    vs.stop()
else:
    vs.release()

cv2.destroyAllWindows()
