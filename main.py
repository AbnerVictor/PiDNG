from DNG.DNG import smv_dng
from DNG.utils import dngTile
import numpy as np
import matplotlib.pyplot as plt
import cv2

if __name__ == '__main__':
    # dng_path = '../extras/IMG_4155.dng'
    # dng_path = '../extras/IMG_4155_dummy.dng'

    # LOAD NPY
    data = np.load('extras/raw_deblur/M03-1318_000065.npy')
    print(data.shape)

    # LOAD DNG
    dng_path = 'extras/raw_deblur/M03-1318_000065.dng'
    my_dng = smv_dng(dng_path, verbose=False)

    # READ Tiles
    print(my_dng.IFDTiles)
    tile = my_dng.IFDTiles[8]
    assert isinstance(tile, dngTile)
    print(tile.tileWidth, tile.tileLength, tile.byteCounts)

    # WRITE DNG
    # my_dng.write('extras/raw_deblur/M03-1318_000065_dummy.dng')

    plt.show(block=True)