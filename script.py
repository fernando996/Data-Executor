import os
import argparse
import ffmpeg

CONFIGS = ["width","height", "display_aspect_ratio","avg_frame_rate", "duration"]
# FILTERS = {"fps":[25,20,15,10,5,3,2,1], "width": [1920, 1280, 640, 480,240]}
FILTERS = {"fps":[25,2,1], "scale": [ {"w":1920, "h": 1080}, {"w":1280, "h": 720} , {"w":640, "h": 480} ]}


ap = argparse.ArgumentParser()

ap.add_argument("-d", "--directory", required=True,
    help="path to directory with files")

# ap.add_argument("-o", "--output", type=str,
#     help="path to optional output video file")
# ap.add_argument("-dl", "--detection-line", type=float, default=0.5,
#     help="detection line height in percentage (default: 0.5)")
# ap.add_argument("-s", "--skip-frames", type=int, default=30,
#     help="# of skip frames between detections")

args = vars(ap.parse_args())

# Get the list of all files and directories
dir_list = os.listdir(args["directory"])
 

# prints all files
# print(dir_list)

files = [] 


# def check_if_video(path):
#     metadata = get_metadata(path)
#     return metadata['codec_type'] == 'video'

# def get_metadata(path):
#     print(path)
#     return ffmpeg.probe(path, select_streams = "v")['streams'][0]

def getMetadata(filePath):
    return ffmpeg.probe(filePath, select_streams = "v")['streams'][0]

def fileHasVideoStream(file_path):
     # video_stream = ffmpeg.probe(filePath, select_streams='v')['streams']
    try:
        video_stream = getMetadata(file_path)
        if video_stream:
            return True
        return False
    except ffmpeg.Error as e:
        return False
        print("output")
        print(e.stdout)
        print("err")
        print(e.stderr)
    
def videoConvert(filePath, w, h, fps=25):
    try:
        input_vid = ffmpeg.input(filePath)
        return (
            input_vid
            .filter('scale', w = w, h = h)
            .filter('fps', fps=fps, round='up')
            .output(str(fps) + str(w)+ str(h) + 'output.mp4')
            .overwrite_output()
            .run()
        )
    except ffmpeg.Error as e:
        # return False
        print("output")
        print(e.stdout)
        print("err")
        print(e.stderr)

    
# Listar os ficheiros de uma diretoria
for entry in os.scandir(args["directory"]):
    if entry.is_file():
        files.append(entry.path)

# Processar os ficheiros
for f in files:
    if fileHasVideoStream(f):
        metaData = getMetadata(f)
        fileObj = {}
        for l in CONFIGS:
            fileObj[l] = metaData[l]

        for fps in FILTERS["fps"]:
            for width in FILTERS["scale"]:
                # print(width)

                videoConvert(f, width["w"], width["h"], fps)
                # input_vid = ffmpeg.input(f)
                # vid = (
                #     input_vid
                #     .filter('scale', w = width["w"], h = width["h"])
                #     .filter('fps', fps=fps, round='up')
                #     .output(str(fps) + str(width) + 'output.mp4')
                #     .overwrite_output()
                #     .run()
                # )

        

        # stream = ffmpeg.input(f)
        # stream = ffmpeg.hflip(stream)
        # stream = ffmpeg.output(stream, 'output.mp4')
        # # ffmpeg.run(stream)
        #  'width': 1024, 'height': 576, 'coded_width': 1024, 'coded_height': 576, 


        # 'codec_name': 'h264',
        # 'codec_long_name': 'H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10', 
        # 'profile': 'High',
        # 'display_aspect_ratio': '16:9',
        # 'r_frame_rate': '25/1'
        # 'avg_frame_rate': '25/1',
        # duration
        # 'duration_ts': 205290000, 'duration': '2281.000000',
        # 'bit_rate': '2091719', 'bits_per_raw_sample': '8', 

# https://github.com/kkroening/ffmpeg-python
# https://github.com/kkroening/ffmpeg-python/tree/master/examples#audiovideo-pipeline