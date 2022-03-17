from DNG.dng import smv_dng
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
    my_dng = smv_dng(raw_pth, verbose=True)

    # READ Tiles
    print(my_dng.IFDTiles)
    for tile_id, tile in my_dng.IFDTiles.items():
        assert isinstance(tile, dngTile)
        print(tile_id, tile.tileWidth, tile.tileLength, tile.tileCount(), tile.dataLen())

        # 16bits 图像
        # 6400 * 4352
        # tmp = open(os.path.join(root, 'tmp.jpg'), 'w+b')
        width = 6400
        height = 4352
        n_w = int(np.ceil(width / tile.tileWidth[0]))
        n_h = int(np.ceil(height / tile.tileLength[0]))

        try:
            tiles = []
            for i in range(len(tile.offset)):
                # tmp.write(tile.data[i])

                # if Uncompressed
                # raw_data = np.frombuffer(tile.data[i], dtype=np.uint16)
                # raw_data = raw_data.reshape(tile.tileLength[0], tile.tileWidth[0])

                # # 替换数据
                # data = data.flatten().astype(np.uint16)
                # print(data.shape)
                # data = data.tobytes()
                # tile.data = [data]
                # my_dng.IFDTiles[tile_id] = tile

                # if compression = 7 or 34892 -> jpeg
                # should be lossless JPEG
                raw_data = pylibjpeg.decode(tile.data[i])
                raw_data = raw_data.reshape(tile.tileLength[0], tile.tileWidth[0])
                tiles.append(raw_data)

            tiles = np.array(tiles).reshape(n_h, n_w, tile.tileLength[0], tile.tileWidth[0])
            tiles = tiles.transpose(0, 2, 1, 3).reshape(n_h * tile.tileLength[0], n_w * tile.tileWidth[0])

            np.save(os.path.join(root, name+'_raw.npy'), tiles)

            plt.figure()
            plt.title('raw')
            plt.imshow(tiles, cmap='gray')
            plt.show(block=True)


        except Exception as e:
            raise (e)

        break

    # WRITE DNG
    my_dng.write(os.path.join(root, name+'_mod.dng'))

