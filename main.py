from DNG.DNG import smv_dng
from DNG.utils import dngTile
import numpy as np
import matplotlib.pyplot as plt
import cv2
import pylibjpeg

from PIL import Image
from io import BytesIO

import os


if __name__ == '__main__':
    # dng_path = '../extras/IMG_4155.dng'
    # dng_path = '../extras/IMG_4155_dummy.dng'

    root = r'C:\Users\abner.yang\Downloads\raw_4097'
    name = 'IMG_4097'

    npy_pth = os.path.join(root, name+'.npy')
    raw_pth = os.path.join(root, name+'.dng')

    # LOAD NPY
    # data = np.load(npy_pth)[0, ...]
    # print(data.shape)
    #
    # plt.figure()
    # plt.title('deblur')
    # plt.imshow(data, cmap='gray')

    # LOAD DNG
    my_dng = smv_dng(raw_pth, verbose=False)

    # READ Tiles
    print(my_dng.IFDTiles)
    for tile_id, tile in my_dng.IFDTiles.items():
        assert isinstance(tile, dngTile)
        print(tile.tileWidth, tile.tileLength, tile.tileCount(), tile.dataLen())

        # 16bits 图像
        # 6400 * 4352
        # tmp = open(os.path.join(root, 'tmp.jpg'), 'w+b')

        try:
            for i in range(len(tile.offset)):
                # tmp.write(tile.data[i])

                # print(tile.byteCounts[i])
                raw_data = pylibjpeg.decode(tile.data[i])
                raw_data = raw_data.reshape(tile.tileLength[0], -1)

                # raw_data = np.frombuffer(tile.data[i], dtype=np.uint16)
                # raw_data = raw_data.reshape(tile.tileLength[0], tile.tileWidth[0])

                plt.figure()
                plt.title('raw')
                plt.imshow(raw_data, cmap='gray')
                plt.show(block=True)

                # # 替换数据
                # data = data.flatten().astype(np.uint16)
                # print(data.shape)
                # data = data.tobytes()
                # tile.data = [data]
                # my_dng.IFDTiles[tile_id] = tile

            # tmp.close()
            # input('s')

        except Exception as e:
            raise (e)


    # WRITE DNG
    my_dng.write(os.path.join(root, name+'_mod.dng'))

