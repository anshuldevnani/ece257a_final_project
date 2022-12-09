import sys
sys.path.append('/usr/local/share/gpac/python')
import libgpac as gpac
import numpy as np
import cv2
import time
from scenarios import *


#initialize gpac
gpac.init()
#indicate we want to start with min bw by using global parameters
gpac.set_args(["Ignored", "--start_with=min_bw"])

#out = cv2.VideoWriter('./test_agg.mp4',cv2.VideoWriter_fourcc(*'mp4v'), 30, (4096,2048))

fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
fps = 30
video_filename = 'baseline.avi'
out = cv2.VideoWriter(video_filename, fourcc, fps, (4096, 2048))

#Our custom DASH adaptation logic
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
        result = test_case2(group,stats)
        return result

# create an instance of the algo (in this example a single dash client is used)
mydash = MyCustomDASHAlgo()


# define a custom filter session monitoring the creation of new filters
class MyFilterSession(gpac.FilterSession):
    def __init__(self, flags=0, blacklist=None, nb_threads=0, sched_type=0):
        gpac.FilterSession.__init__(self, flags, blacklist, nb_threads, sched_type)

    def on_filter_new(self, f):
        # bind the dashin filter to our algorithm object
        if f.name == "dashin":
            f.bind(mydash)


# define a custom filter
class MyFilter(gpac.FilterCustom):
    def __init__(self, session):
        gpac.FilterCustom.__init__(self, session, "PYRawVid")
        # indicate what we accept and produce - here, raw video input only (this is a sink)
        self.push_cap("StreamType", "Visual", gpac.GF_CAPS_INPUT)
        self.push_cap("CodecID", "Raw", gpac.GF_CAPS_INPUT)

        self.max_buffer = 10000000
        self.play_buffer = 3000000
        self.re_buffer = 100000
        self.buffering = True
        #cached packed for grabbing video for GPU decoders
        self.tmp_pck = None

    # configure input PIDs
    def configure_pid(self, pid, is_remove):
        if is_remove:
            return 0
        if pid in self.ipids:
            print('PID reconfigured')
        else:
            print('PID configured')

            #1- setup buffer levels - the max_playout_us and min_playout_us are only informative for the filter session
            #but are forwarded to the DASH algo
            evt = gpac.FilterEvent(gpac.GF_FEVT_BUFFER_REQ)
            evt.buffer_req.max_buffer_us = self.max_buffer
            evt.buffer_req.max_playout_us = self.play_buffer
            evt.buffer_req.min_playout_us = self.re_buffer
            pid.send_event(evt)

            #2-  we are a sink, we MUST send a play event
            evt = gpac.FilterEvent(gpac.GF_FEVT_PLAY)
            pid.send_event(evt)

        # get width, height, stride and pixel format - get_prop may return None if property is not yet known
        # but this should not happen for these properties with raw video, except StrideUV which is NULL for non (semi) planar YUV formats
        self.width = pid.get_prop('Width')
        self.height = pid.get_prop('Height')
        self.pixfmt = pid.get_prop('PixelFormat')
        self.stride = pid.get_prop('Stride')
        self.stride_uv = pid.get_prop('StrideUV')
        self.timescale = pid.get_prop('Timescale')
        return 0

    # process
    def process(self):
		#only one PID in this example
        for pid in self.ipids:

            title = 'GPAC cv2'
            if pid.eos:
                pass
            #not done, check buffer levels
            else:
                buffer = pid.buffer
                if self.buffering:
                    #playout buffer not yet filled
                    if buffer < self.play_buffer:
                        pc = 100 * buffer / self.play_buffer
                        title += " - buffering " + str(int(pc)) + ' %'
                        break

                    #playout buffer refilled
                    title += " - resuming"
                    self.buffering = False

                if self.re_buffer:
                    #playout buffer underflow 
                    if buffer < self.re_buffer:
                        title += " - low buffer, pausing"
                        self.buffering = True
                        break

                #show max buffer level 
                if self.max_buffer > self.play_buffer:
                        pc = buffer / self.max_buffer * 100
                        title += " - buffer " + str(int(buffer/1000000)) + 's ' + str(int(pc)) + ' %'

            pck = pid.get_packet()
            if pck is None:
                break

            #frame interface, data is in GPU memory or internal to decoder, try to grab it
            #we do so by creating a clone of the packet, reusing the same clone at each call to reduce memory allocations
            if pck.frame_ifce:
                self.tmp_pck = pck.clone(self.tmp_pck)
                if self.tmp_pck == None:
                    raise Exception("Packet clone failed")
                data = self.tmp_pck.data
            else:
                data = pck.data

            #convert to cv2 image for some well known formats
            #note that for YUV formats here, we assume stride luma is width and stride chroma is width/2
            if self.pixfmt == 'nv12':
                yuv = data.reshape((self.height * 3 // 2, self.width))
                rgb = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB_NV12)
            elif self.pixfmt == 'yuv':
                yuv = data.reshape((self.height * 3 // 2, self.width))
                rgb = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB_I420)
            elif self.pixfmt == 'rgba':
                rgb = data.reshape((self.height, self.width, 4))
            elif self.pixfmt == 'rgb':
                rgb = data.reshape((self.height, self.width, 3))
            else:
                print('Unsupported pixel format ' + self.pixfmt)
                quit()

            print((cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR).shape))
            out.write(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
            #print(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
            cv2.imshow('frame', cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
            cv2.setWindowTitle('frame', title)

            # #get packet duration for later sleep
            # dur = pck.dur
            # dur /= self.timescale
            
            pid.drop_packet()

            k = cv2.waitKey(1)
            #press 'esc' to abort
            if (k == 27):
                fs.abort()


            # dummy player, this does not take into account the time needed to draw the frame, so we will likely drift
            # time.sleep(dur)

        return 0


if __name__ == '__main__':
    #create a custom filter session
    fs = MyFilterSession()

    # load a source filter
    #if a parameter is passed to the script, use this as source
    if len(sys.argv) > 1:
        src = fs.load_src(sys.argv[1])
    #otherwise load one of our DASH sequences
    else:
        src = fs.load_src("http://172.30.40.151/out/dash_tiled.mpd:gpac:start_with=min_bw")
    # load our custom filter and assign its source
    my_filter = MyFilter(fs)
    my_filter.set_source(src)

    # and run
    fs.run()

    fs.print_graph()
    
    fs.delete()
    # out.release()
    gpac.close()
