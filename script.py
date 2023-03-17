import os
import argparse
import MediaInfo

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
 
print("Files and directories in '", args["directory"], "' :")
 
# prints all files
# print(dir_list)

files = [] 

# Listar os ficheiros de uma diretoria
for entry in os.scandir(args["directory"]):
    if entry.is_file():
        files.append(entry.name)
print(files)

for f in files:
    fileInfo = MediaInfo.parse(f)
    for track in fileInfo.tracks:
        if track.track_type == "Video":
            print(files)


import ffmpeg

def check_if_video(path):
    metadata = get_metadata(path)
    return metadata['codec_type'] == 'video'

def get_metadata(path):
    return ffmpeg.probe(path, select_streams = "v")['streams'][0]