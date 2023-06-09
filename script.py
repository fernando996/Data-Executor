import os
import argparse
import ffmpeg
import config
import subprocess
import time
import csv

ap = argparse.ArgumentParser()

ap.add_argument("-d", "--directory", required=True,
                help="path to directory with files")

# ap.add_argument("-o", "--output", type=str,
#     help="path to optional output video file")
# ap.add_argument("-dl", "--detection-line", type=float, default=0.5,
#     help="detection line height in percentage (default: 0.5)")
# ap.add_argument("-s", "--skip-frames", type=int, default=30,
#     help="# of skip frames between detections")


# def check_if_video(path):
#     metadata = get_metadata(path)
#     return metadata['codec_type'] == 'video'

# def get_metadata(path):
#     print(path)
#     return ffmpeg.probe(path, select_streams = "v")['streams'][0]

def getMetadata(filePath):
    return ffmpeg.probe(filePath, select_streams="v")['streams'][0]


def fileHasVideoStream(file_path):
    try:
        video_stream = getMetadata(file_path)
        if video_stream:
            return True
        return False
    except ffmpeg.Error as e:
        return False


def videoConvert(filePath, w, h, fps=25):
    try:
        input_vid = ffmpeg.input(filePath)
        fileName = os.path.basename(filePath)
        convFileName = os.path.join(
            'output', "%sx%s_%s_%s" % (w, h, fps, fileName))
        (
            input_vid
            .filter('scale', w=w, h=h)
            .filter('fps', fps=fps, round='up')
            .output(convFileName)
            .overwrite_output()
            .run()
        )
        return convFileName
    except ffmpeg.Error as e:
        return False
        print("output")
        print(e.stdout)
        print("err")
        print(e.stderr)


def processVideo(filePath, params):
    st = time.time()
    subprocess.run(["python", config.scriptLocation] +
                   config.scriptParamsFixed + params + ["-i", filePath])
    et = time.time()
    return et - st


def getProccessData():
    if os.path.exists(config.outputFilePath) is False or os.stat(config.outputFilePath).st_size == 0:
        return {'down': 0, 'up': 0}

    with open(config.outputFilePath, "r") as file:
        lastLine = file.readlines()[-1].replace("\n", "")
        lastLine = lastLine.split(";")
        obj = {'down': lastLine[-2:-1][0], 'up': lastLine[-1:][0]}
        return obj


def getParams(param):
    _params = []
    for k, v in param.items():
        _params = _params + [k] + [v]
    return _params


def getFileHeaders():
    return config.metadataProps + \
        ["fps", "c_width", "c_heigth", "filename", "fName", "up", "down", "elapsedTime"] + \
        [k for k in config.scriptParams[0]]


def writeFileHeaders():
    with open(config.runsOutputFileName, 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, getFileHeaders())
        writer.writeheader()
        f.close()


def writeFileRow(row):
    with open(config.runsOutputFileName, 'a', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, getFileHeaders())
        writer.writerow(row)
        f.close()


def main():
    args = vars(ap.parse_args())

    writeFileHeaders()

    files = []

    # Listar os ficheiros de uma diretoria
    for entry in os.scandir(args["directory"]):
        if entry.is_file():
            files.append(entry.path)

    # Processar os ficheiros
    for f in files:

        # Check if is a video file
        if fileHasVideoStream(f):
            metaData = getMetadata(f)
            fileObj = {}
            for l in config.metadataProps:
                fileObj[l] = metaData[l]

            # Convert options
            for fps in config.fps:
                fileObj["fps"] = fps
                for width in config.scale:
                    fileObj["c_width"] = width["w"]
                    fileObj["c_heigth"] = width["h"]

                    fileObj["filename"] = f

                    fName = videoConvert(f, width["w"], width["h"], fps)
                    fileObj["fName"] = f

                    for param in config.scriptParams:

                        elapsed_time = processVideo(fName, getParams(param))

                        fileObj = {**fileObj, **getProccessData(), **
                                   param, "elapsedTime": elapsed_time}

                        if os.path.exists(config.outputFilePath):
                            os.remove(config.outputFilePath)

                        writeFileRow(fileObj)
                    # Delete converted file
                    if os.path.exists(fName):
                        os.remove(fName)


if __name__ == "__main__":
    main()

    # subprocess.run(["python"] + [config.scriptLocation] + config.scriptParams)

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
