import sys
sys.path.append('/usr/local/share/gpac/python')
import datetime
import types
import sys
import time
import numpy as np
import libgpac as gpac
from scenarios import *
print("Welcome to GPAC Python !\nVersion: " + gpac.version + "\n" + gpac.copyright_cite)

gpac.init()


class MyCustomDASHAlgo:
    def on_period_reset(self, type):
        print('period reset type ' + str(type))

    def on_new_group(self, group):
        print('new group ' + str(group.idx) + ' qualities ' + str(len(group.qualities)) + ' codec ' + group.qualities[0].codec + ' SRD ' + str(group.SRD.x) + 'x' + str(group.SRD.y));
        group.active = True
        if group.qualities[0].codec.startswith("hvt"):
            group.tile = True
        else:
            group.tile = False

    def on_rate_adaptation(self, group, base_group, force_low_complexity, stats):
        #result = test_case1(group,stats)
        #result = test_case2(group,stats)
        #result = test_case3(group,stats)
        result = test_case4(group,stats)
        return result


mydash = MyCustomDASHAlgo()

#define a custom filter
class MyFilterSession(gpac.FilterSession):
    def __init__(self, flags=0, blacklist=None, nb_threads=0, sched_type=0):
        gpac.FilterSession.__init__(self, flags, blacklist, nb_threads, sched_type)

    def on_filter_new(self, f):
        if f.name == "dashin":
            print("Binding DASH algo ")
            f.bind(mydash)

#create a session
fs = MyFilterSession(0)

f1 = fs.load_src("http://172.30.40.151/out/dash_tiled.mpd")
f2 = fs.load("dashin:start_with=min_bw")
f3 = fs.load("tileagg")
#load a sink
f4 = fs.load("vout")#:speed=0.45")

f2.set_source(f1)
f3.set_source(f2)
f4.set_source(f3)

#run the session in blocking mode
btime = time.time()
fs.run()

print(f'Done, executing time: {time.time() - btime}')

fs.delete()
gpac.close()
