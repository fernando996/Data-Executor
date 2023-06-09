metadataProps = ["width", "height",
                 "display_aspect_ratio", "avg_frame_rate", "duration"]
fps = [25, 15, 10, 5, 2, 1]
scale = [{"w": 1920, "h": 1080}, {"w": 1280, "h": 720}, {"w": 640, "h": 480}]
scriptLocation = r"C:\Users\Fernando\Desktop\Cam\cam_counter_deliverable\cam_counter\people_counter.py"
scriptParamsFixed = ["-p", r"C:\Users\Fernando\Desktop\Cam\cam_counter_deliverable\cam_counter\models\MobileNetSSD_deploy.prototxt",
                     "-m", r"C:\Users\Fernando\Desktop\Cam\cam_counter_deliverable\cam_counter\models\MobileNetSSD_deploy.caffemodel"]
scriptParams = [{"-fw": "500", "--confidence": "0.4",  "-ss": "0"},
                {"-fw": "600", "--confidence": "0.4",  "-ss": "0"},
                {"-fw": "720", "--confidence": "0.4",  "-ss": "0"},
                {"-fw": "1080", "--confidence": "0.4",  "-ss": "0"},
                {"-fw": "1920", "--confidence": "0.4",  "-ss": "0"},
                {"-fw": "4000", "--confidence": "0.4",  "-ss": "0"},
                {"-fw": "500", "--confidence": "0.8",  "-ss": "0"},
                {"-fw": "600", "--confidence": "0.8",  "-ss": "0"},
                {"-fw": "720", "--confidence": "0.8",  "-ss": "0"},
                {"-fw": "1080", "--confidence": "0.8",  "-ss": "0"},
                {"-fw": "1920", "--confidence": "0.8",  "-ss": "0"},
                {"-fw": "4000", "--confidence": "0.8",  "-ss": "0"},
                ]
outputFilePath = r".\output\global_log.csv"
runsOutputFileName = r"runs.csv"
# -dl 0.85
