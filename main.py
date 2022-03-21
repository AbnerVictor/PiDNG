from DNG.Editor import DNGEditor, get_int_tag_value
from DNG.utils import Tag
from DNG.dng import smv_dng
import numpy as np
import logging

import os
import matplotlib.pyplot as plt

if __name__ == '__main__':

    logging.basicConfig(level=logging.WARNING)

    root = r'C:\Users\abner.yang\Downloads\raw_4097'
    name = 'IMG_4097'
    raw_pth = os.path.join(root, name + '.dng')
    out_pth = os.path.join(root, name + '_mod' + '.dng')
    npy_pth = os.path.join(root, name + '_raw.npy')

    dng_file = smv_dng(raw_pth, verbose=False)

    my_dng = DNGEditor(dng_file)
    active_tile = my_dng.extract_CFA()
    # np.save(npy_pth, active_tile)

    BlackLevel = get_int_tag_value(my_dng.CFA_IFD, tag_id=Tag.BlackLevel, endian=my_dng.endian)
    print('blacklevel:', BlackLevel)

    npy_data = np.load(npy_pth)
    print(f'npy shape: {npy_data.shape}')

    assert active_tile.shape == npy_data.shape

    my_dng.write_CFA(npy_data, compression=1)
    my_dng.write(out_pth)

    plt.figure()
    plt.title('raw')
    plt.imshow(active_tile, cmap='gray')

    plt.figure()
    plt.title('output')
    plt.imshow(npy_data, cmap='gray')

    plt.show(block=True)
