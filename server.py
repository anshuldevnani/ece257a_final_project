import argparse
import os
from subprocess import call

def dir_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise FileNotFoundError

def rep_list(string):
    return string.split(",")




parser = argparse.ArgumentParser()
parser.add_argument('--path', type=dir_path)
parser.add_argument('--reps', type=rep_list)
parser.add_argument('--segment_duration', type=int)
parser.add_argument('--width', type=int)
parser.add_argument('--height', type=int)
parser.add_argument('--slices', type=int)
parser.add_argument('--fps', type=int)
args = parser.parse_args()




for rep in args.reps:
    command  = "kvazaar -i {} --input-res {}x{} -o output_{}.hvc --tiles {}x{} --slices tiles --mv-constraint frametilemargin --bitrate {} --input-fps {}".format(args.path, args.width, args.height, rep, args.slices, args.slices, rep, args.fps)
    os.system(command)

temp_list = []
for rep in args.reps:
    command = "MP4Box -add output_{}.hvc:split_tiles -new video_tiled_{}.mp4".format(rep, rep)
    temp_list.append("video_tiled_{}.mp4".format(rep))
    os.system(command)


videos= " ".join(temp_list)


print(videos)
command = "MP4Box -dash {} -profile live -out ./out/dash_tiled.mpd {}".format(args.segment_duration * 1000, videos)
os.system(command)
print(command)

