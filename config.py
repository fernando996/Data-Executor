metadataProps = ["width", "height",
                 "display_aspect_ratio", "avg_frame_rate", "duration"]
fps = [25, 2, 1]
scale = [{"w": 1920, "h": 1080}, {"w": 1280, "h": 720}, {"w": 640, "h": 480}]
scriptLocation = r"C:\Users\fernandom\Desktop\Cam\cam_counter_deliverable\cam_counter\people_counter.py"
scriptParamsFixed = ["-p", r"C:\Users\fernandom\Desktop\Cam\cam_counter_deliverable\cam_counter\models\MobileNetSSD_deploy.prototxt",
                     "-m", r"C:\Users\fernandom\Desktop\Cam\cam_counter_deliverable\cam_counter\models\MobileNetSSD_deploy.caffemodel"]
scriptParams = [{"-fw": "500", "--confidence": "0.4",  "-ss": "0"},
                {"-fw": "600", "--confidence": "0.4",  "-ss": "0"}]
outputFilePath = r".\output\global_log.csv"
# -dl 0.85
