# Bitrates
# 0 - .1 Mbps
# 1 - .25 Mbps
# 2 - .5 Mbps
# 3 - 1.0 Mbps
# 4 - 2.5 Mbps
# 5 - 5.0 Mbps



# all tiles streamed at lowest bitrate
def test_case1():
    if not group.tile:
        print('Download Rate - {} Buffer Min - {} Buffer Max - {} Buffer {}'.format(stats.total_rate, stats.buffer_min, stats.buffer_max, stats.buffer))
        return 0
    if group.tile:
        return 0

# all tiles at the highest bitrate
def test_case2(group, stats):
    if not group.tile:
        print('Download Rate - {} Buffer Min - {} Buffer Max - {} Buffer {}'.format(stats.total_rate, stats.buffer_min, stats.buffer_max, stats.buffer))
        return 0
    if group.tile:
        return 5

def test_case3(group,stats):
    newq = 0
    if not group.tile:
        print('Download Rate - {} Buffer Min - {} Buffer Max - {} Buffer {}'.format(stats.total_rate, stats.buffer_min, stats.buffer_max, stats.buffer))
    if group.tile:
        if(group.idx == 1 or  group.idx == 3 or group.idx == 7 or group.idx == 9):
            newq = 0
        else:
            newq = 5
    
    return newq

def test_case4(group, stats):
    newq = 0
    if not group.tile:
        print('Download Rate - {} Buffer Min - {} Buffer Max - {} Buffer {}'.format(stats.total_rate, stats.buffer_min, stats.buffer_max, stats.buffer))
    if group.tile:
        if(group.idx == 1 or  group.idx == 3 or group.idx == 7 or group.idx == 9):
            newq = 0
        else:
            newq = stats.active_quality_idx + 1
    
    return newq


