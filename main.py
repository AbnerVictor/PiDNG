from DNG.Editor import DNGEditor, get_digit_tag_value
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
    npy_pth = os.path.join(root, name + '_0322.npy')

    dng_file = smv_dng(raw_pth, verbose=False)

    my_dng = DNGEditor(dng_file)
    active_tile = my_dng.extract_CFA()
    # np.save(npy_pth, active_tile)

    BlackLevel = get_digit_tag_value(my_dng.CFA_IFD, tag_id=Tag.BlackLevel, endian=my_dng.endian)
    WhiteLevel = get_digit_tag_value(my_dng.CFA_IFD, tag_id=Tag.WhiteLevel, endian=my_dng.endian)[0]
    print('blacklevel:', BlackLevel, '; whitelevel:', WhiteLevel)

    npy_data = np.load(npy_pth)
    print(f'npy shape: {npy_data.shape}')

    # max_val = np.max(np.max(active_tile))
    max_val = WhiteLevel - BlackLevel[0]

    print('CFA max:', active_tile.min(), 'CFA min:', active_tile.max())

    # active_tile_fp32 = np.clip(np.array((active_tile - BlackLevel[0]) / max_val, dtype=np.float32), 0.0, 1.0)
    # print(active_tile_fp32.min(), active_tile_fp32.max())
    # active_tile_uint16 = np.array(np.clip(np.floor(active_tile_fp32 * max_val + BlackLevel[0]),
    #                                       BlackLevel[0], WhiteLevel), dtype=np.uint16)
    # print(active_tile_uint16.min(), active_tile_uint16.max())
    #
    # plt.figure()
    # plt.title('output')
    # plt.imshow(active_tile_uint16, cmap='gray')

    assert active_tile.shape == npy_data.shape
    print('NPY max:', npy_data.min(), 'NPY min:', npy_data.max())


    plt.figure()
    plt.title('raw')
    plt.imshow(active_tile, cmap='gray')

    # my_dng.write_CFA(active_tile_uint16, compression=1)
    # my_dng.write(out_pth)

    plt.show(block=True)
