from DNG.DNG import smv_dng
from DNG.utils import dngTile
import numpy as np
import matplotlib.pyplot as plt
import cv2

if __name__ == '__main__':
    # dng_path = '../extras/IMG_4155.dng'
    # dng_path = '../extras/IMG_4155_dummy.dng'

    # LOAD NPY
    data = np.load('extras/raw_deblur/M03-1318_000065.npy')[0, ...]
    print(data.shape)

    plt.figure()
    plt.title('deblur')
    plt.imshow(data, cmap='gray')

    # LOAD DNG
    dng_path = 'extras/raw_deblur/M03-1318_000065.dng'
    my_dng = smv_dng(dng_path, verbose=False)

    # READ Tiles
    print(my_dng.IFDTiles)
    tile = my_dng.IFDTiles[8]
    assert isinstance(tile, dngTile)
    print(tile.tileWidth, tile.tileLength, tile.byteCounts)
    # 16bits 图像
    raw_data = np.frombuffer(tile.data[0], dtype=np.uint16)
    raw_data = raw_data.reshape(tile.tileLength[0], tile.tileWidth[0])

    plt.figure()
    plt.title('raw')
    plt.imshow(raw_data, cmap='gray')

    data = data.flatten().astype(np.uint16)
    print(data.shape)

    data = data.tobytes()

    tile.data = [data]
    my_dng.IFDTiles[8] = tile

    # WRITE DNG
    my_dng.write('extras/raw_deblur/M03-1318_000065_deblur.dng')

    plt.show(block=True)