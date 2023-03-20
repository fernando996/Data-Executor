metadataProps = ["width", "height",
                 "display_aspect_ratio", "avg_frame_rate", "duration"]
fps = [25, 2, 1]
scale = [{"w": 1920, "h": 1080}, {"w": 1280, "h": 720}, {"w": 640, "h": 480}]
scriptLocation = r"C:\Users\fernandom\Desktop\Cam\cam_counter_deliverable\cam_counter\people_counter.py"
scriptParams = ["-cam", "0", "-fw", "500", "--confidence", "0.4",  "-ss", "0", "-p", r"C:\Users\fernandom\Desktop\Cam\cam_counter_deliverable\cam_counter\models\MobileNetSSD_deploy.prototxt",
                "-m", r"C:\Users\fernandom\Desktop\Cam\cam_counter_deliverable\cam_counter\models\MobileNetSSD_deploy.caffemodel"]
