from DNG.Editor import DNGEditor, get_digit_tag_value
from DNG.utils import Tag
from DNG.dng import smv_dng
import numpy as np
import logging

import os
import matplotlib.pyplot as plt

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    root = r'\\192.168.100.201\Media-Dev\Experiment_Log\xin.yang\Experiment_backup\DNG_RAW'
    name = 'IMG_4097_mod'
    raw_pth = os.path.join(root, name + '.dng')
    out_pth = os.path.join(root, name + '_mod' + '.dng')
    npy_pth = os.path.join(root, name + '_0322.npy')

    dng_file = smv_dng(raw_pth, verbose=False)

    my_dng = DNGEditor(dng_file)
    active_tile = my_dng.extract_CFA()
    # np.save(npy_pth, active_tile)

    # npy_data = np.load(npy_pth)
    # print(f'npy shape: {npy_data.shape}')
    #
    # assert active_tile.shape == npy_data.shape
    # print('NPY min:', npy_data.min(), 'NPY max:', npy_data.max())

    BlackLevel = get_digit_tag_value(my_dng.CFA_IFD, tag_id=Tag.BlackLevel, endian=my_dng.endian)
    WhiteLevel = get_digit_tag_value(my_dng.CFA_IFD, tag_id=Tag.WhiteLevel, endian=my_dng.endian)[0]
    LinearizationTable = get_digit_tag_value(my_dng.CFA_IFD, tag_id=Tag.LinearizationTable, endian=my_dng.endian)
    max_val = WhiteLevel - BlackLevel[0]

    print('blacklevel:', BlackLevel, '; whitelevel:', WhiteLevel)
    print('linearization table:', LinearizationTable)
    print('CFA min:', active_tile.min(), 'CFA max:', active_tile.max())

    active_tile_fp32 = np.clip(np.array((active_tile - BlackLevel[0]) / max_val, dtype=np.float32), 0.0, 1.0)
    print('Linear CFA min:', active_tile_fp32.min(), 'Linear CFA max:', active_tile_fp32.max())

    active_tile_uint16 = np.array(np.clip(np.floor(active_tile_fp32 * max_val + BlackLevel[0]),
                                          BlackLevel[0], WhiteLevel), dtype=np.uint16)
    print('Recovered CFA min:', active_tile_uint16.min(), 'Recovered CFA max:', active_tile_uint16.max())

    plt.figure()
    plt.title('raw')
    plt.imshow(active_tile, cmap='gray')

    plt.figure()
    plt.title('output')
    plt.imshow(active_tile_fp32, cmap='gray')

    plt.figure()
    plt.title('output')
    plt.imshow(active_tile_uint16, cmap='gray')

    my_dng.write_CFA(active_tile, compression=1)
    my_dng.write(out_pth)

    plt.show(block=True)
