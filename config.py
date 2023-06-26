metadataProps = ["width", "height",
                 "display_aspect_ratio", "avg_frame_rate", "duration"]
# fps = [25]
scale = [{"w": 1080, "h": 1920}]
scriptLocation = r"/home/fernando/projetos/cam_counter/people_counter.py"
scriptParamsFixed = ["-p", r"/home/fernando/projetos/cam_counter/models/MobileNetSSD_deploy.prototxt",
                     "-m", r"/home/fernando/projetos/cam_counter/models/MobileNetSSD_deploy.caffemodel"]
scriptParams = [{"-fw": "500", "--confidence": "0.5",  "-ss": "0", "-dl":"0.5"},
                {"-fw": "500", "--confidence": "0.5",  "-ss": "0", "-dl":"0.4"},
                {"-fw": "500", "--confidence": "0.5",  "-ss": "0", "-dl":"0.3"},
                {"-fw": "500", "--confidence": "0.5",  "-ss": "0", "-dl":"0.2"},
                {"-fw": "500", "--confidence": "0.5",  "-ss": "0", "-dl":"0.6"},
                {"-fw": "500", "--confidence": "0.5",  "-ss": "0", "-dl":"0.7"},
                {"-fw": "500", "--confidence": "0.5",  "-ss": "0", "-dl":"0.8"},
                {"-fw": "1080", "--confidence": "0.5",  "-ss": "0", "-dl":"0.3"},
                ]
outputFilePath = r"./output/global_log.csv"
runsOutputFileName = r"runs.csv"
