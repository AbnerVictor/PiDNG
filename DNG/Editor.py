from DNG.dng import smv_dng
from DNG.utils import dngTag, dngIFD, dngTile, dngStrip, Tag
import struct
import pylibjpeg
import numpy as np
import logging

def get_tags(ifd: dngIFD, tag_id: tuple):
    for tag in ifd.tags:
        assert isinstance(tag, dngTag)
        if tag.TagId == tag_id[0]:
            yield (ifd, tag)

        if tag.subIFD is not None:
            for sub_ifd in tag.subIFD:
                for tag_ in get_tags(sub_ifd, tag_id):
                    yield tag_


def get_int_tag_value(ifd: dngIFD, tag_id: tuple, endian='little'):
    try:
        tag = get_tags(ifd=ifd, tag_id=tag_id).__next__()[1]
        type = tag_id[1]
        byte_len = len(tag.Value)
        data = []
        for i in range(0, byte_len, type[1]):
            data.append(int.from_bytes(tag.Value[i: i+type[1]], byteorder=endian))
        return data
    except Exception as e:
        return None


def get_tag_value(ifd: dngIFD, tag_id: tuple):
    try:
        tag = get_tags(ifd=ifd, tag_id=tag_id).__next__()[1]
        return tag.Value
    except Exception as e:
        return None


def load_tile(tile: dngTile, ImageWidth=0, ImageLength=0, compression=1, dtype=np.uint16):
    try:
        assert compression == 7 or compression == 34892 or compression == 1
        tiles = []
        w = tile.tileWidth[0]
        h = tile.tileLength[0]

        n_h = int(np.ceil(ImageLength / h)) if int(np.ceil(ImageLength / h)) != 0 else 1
        n_w = int(np.ceil(ImageWidth / w)) if int(np.ceil(ImageWidth / w)) != 0 else 1

        for data in tile.data:
            if compression == 7 or compression == 34892:
                tile_ = pylibjpeg.decode(data)
                tile_.reshape(w, h)
            elif compression == 1:
                tile_ = np.frombuffer(tile.data, dtype=dtype)
                tile_.reshape(w, h)
            tiles.append(tile_)

        tiles = np.array(tiles).reshape(n_h, n_w, h, w)
        tiles = tiles.transpose(0, 2, 1, 3).reshape(n_h * h, n_w * w)
        return tiles
    except:
        raise NotImplemented(f'Load tiles failed, compression type: {compression}')


class DNGEditor(object):
    def __init__(self, DNG: smv_dng):
        self.dng = DNG
        self.CFA_IFD = None
        self.logger = logging.getLogger('DNGEditor')

    def extract_CFA(self):
        endian = 'little' if self.dng.endian == '<' else 'big'
        CFA_IFD = None
        # travers IFDs
        for NewSubfileType in get_tags(ifd=self.dng.mainIFD, tag_id=Tag.NewSubfileType):
            # print(tag.TagId, tag.Value.decode())
            ifd, tag = NewSubfileType

            flag_full_res = False
            flag_cfa = False

            assert isinstance(tag, dngTag)
            if int.from_bytes(tag.Value, byteorder=endian) == 0:
                # full-resolution-image
                flag_full_res = True

            if get_int_tag_value(ifd=ifd, tag_id=Tag.PhotometricInterpretation)[0] == 32803:
                flag_cfa = True

            if flag_full_res and flag_cfa:
                CFA_IFD = ifd

        if CFA_IFD is None:
            raise Exception('CFA IFD not found.')

        # load IFD param
        self.CFA_IFD = CFA_IFD
        self.logger.debug(f'Load CFA_IFD, IFD offset: {CFA_IFD.ori_offset}')

        Compression = get_int_tag_value(ifd=CFA_IFD, tag_id=Tag.Compression, endian=endian)[0]
        ImageWidth = get_int_tag_value(ifd=CFA_IFD, tag_id=Tag.ImageWidth, endian=endian)[0]
        ImageLength = get_int_tag_value(ifd=CFA_IFD, tag_id=Tag.ImageLength, endian=endian)[0]

        # load Tile param
        ActiveArea = get_int_tag_value(ifd=CFA_IFD, tag_id=Tag.ActiveArea, endian=endian)

        tile = load_tile(self.dng.IFDTiles[CFA_IFD.ori_offset], ImageWidth, ImageLength, Compression, dtype=np.uint16)
        active_tile = tile[ActiveArea[0]:ActiveArea[2], ActiveArea[1]:ActiveArea[3]]

        self.logger.debug(f'Load Tile, tile size: {tile.shape}; Compression: {Compression}')
        self.logger.debug(f'ActiveArea: {ActiveArea}, activeArea shape: {active_tile.shape}')

        return tile, active_tile

if __name__ == '__main__':
    import os
    import matplotlib.pyplot as plt

    logging.basicConfig(level=logging.DEBUG)

    root = r'C:\Users\abner.yang\Downloads\raw_4097'
    name = 'IMG_4097'
    raw_pth = os.path.join(root, name + '.dng')
    dng_file = smv_dng(raw_pth, verbose=False)

    my_dng = DNGEditor(dng_file)
    a, b = my_dng.extract_CFA()

    plt.figure()
    plt.title('raw')
    plt.imshow(b, cmap='gray')
    plt.show(block=True)