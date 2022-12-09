import cv2
import numpy as np
from PIL import Image
import imageio
import pdb
import upscaling

low_frames = []
high_frames = []
low_path = "test_tile_lost.mp4"
high_path = "test_tile_high.mp4" 
low_cap = cv2.VideoCapture(low_path)
high_cap = cv2.VideoCapture(high_path)
ret = True
while ret:
    ret, img = low_cap.read() # read one frame from the 'capture' object; img is (H, W, C)
    if ret:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        low_frames.append(img)
ret = True
while ret:
    ret, img = high_cap.read() # read one frame from the 'capture' object; img is (H, W, C)
    if ret:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        high_frames.append(img)
low_video = np.stack(low_frames, axis=0) # dimensions (T, H, W, C)
high_video = np.stack(high_frames, axis=0) # dimensions (T, H, W, C)
print(low_video.shape)
print(high_video.shape)

batch, height, width, channel = low_video.shape

# Scale factor
ratio = 2
  
# Coefficient
a = -1/2

upscaled_video = np.zeros((batch, height*ratio, width*ratio, channel))
for i in range(batch):
    low_video[i, 320:704, 640:1280,:] = high_video[i, 320:704, 640:1280,:]
    upscaled_video[i, :, :,:] = upscaling.bicubic(low_video[i], ratio, a) 

print('Upscaled: ', upscaled_video.shape)

filename = "saved.mp4"
codec_id = "mp4v" # ID for a video codec.
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(filename, fourcc, 50, (width, height), False)

for frame in np.split(upscaled_video, batch, axis=0):
    out.write(frame)
out.release()

#im = Image.fromarray(low_video[1])
saveimage = low_video[5,:,:,:]
#pdb.set_trace()
#saveimage = np.moveaxis(saveimage, 0, 2)
print(saveimage.shape)
imageio.imwrite("your_file.png", saveimage)

