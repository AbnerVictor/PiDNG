from DNG.Editor import DNGEditor
from DNG.dng import smv_dng
import numpy as np
import logging

import os
import matplotlib.pyplot as plt

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    root = r'C:\Users\abner.yang\Downloads\raw_4097'
    name = 'IMG_4097'
    raw_pth = os.path.join(root, name + '.dng')
    out_pth = os.path.join(root, name + '_mod' + '.dng')
    npy_pth = os.path.join(root, name + '_raw.npy')

    dng_file = smv_dng(raw_pth, verbose=False)

    my_dng = DNGEditor(dng_file)
    active_tile = my_dng.extract_CFA()
    # np.save(npy_pth, active_tile)

    npy_data = np.load(npy_pth)
    print(f'npy shape: {npy_data.shape}')

    assert active_tile.shape == npy_data.shape

    plt.figure()
    plt.title('raw')
    plt.imshow(active_tile, cmap='gray')

    plt.figure()
    plt.title('output')
    plt.imshow(npy_data, cmap='gray')

    my_dng.write_CFA(npy_data)
    my_dng.write(out_pth)
    plt.show(block=True)
