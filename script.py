import os
import argparse

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


files = [f for f in dir_list if os.path.isfile(f)]
for f in dir_list:
    if os.path.isfile(f):
        print(f)


# Listar os ficheiros de uma diretoria
for entry in os.scandir(args["directory"]):
    if entry.is_file():
        print(entry.name)
