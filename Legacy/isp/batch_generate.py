import cv2
from pipeline import run_pipeline, inverse_pipeline
from pipeline_utils import init_tone_map, get_metadata
import os
import numpy as np
import glob
import imageio
import math
from scipy import ndimage
from kernel_generator import *
import rawpy

# meta = get_metadata('F:/NIKON-dngimage/RVD-dngdata/1009/1009/YYT_1138.dng')
# print(meta['noise_profile'])
# a=0
params = {
    'output_stage': 'gamma',  # options: 'normal', 'demosaic', 'white_balance', 'xyz', 'prorgb', 'hue', 'ev', 'hsv_enhance', 'tone', 'sRGB', 'gamma', 'lens_correction', 'denoise'
    'save_as': 'tif',  # options: 'jpg', 'png', 'tif', etc.
    'demosaic_type': 'menon2007',
    'save_dtype': np.uint16
}
files = glob.glob('./canon/*.dng')
tone_fn = init_tone_map()

for file in files:

    clean_rgb_image = (run_pipeline(file, params, tone_fn)*(2**16-1)).astype(np.uint16)
    imageio.imwrite('./oursv4-canon/{}'.format(os.path.basename(file).replace('.dng', '.tif')), clean_rgb_image)

