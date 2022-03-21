from DNG.dng import smv_dng
from DNG.utils import dngTag, dngIFD, dngTile, dngStrip, Tag
import pylibjpeg
from pydicom.encoders import RLELosslessEncoder
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


def get_tag(ifd: dngIFD, tag_id: tuple):
    for tag in ifd.tags:
        assert isinstance(tag, dngTag)
        if tag.TagId == tag_id[0]:
            return (ifd, tag)


def set_tag(tag: dngTag, ifd: dngIFD, tag_id: tuple):
    for i in range(len(ifd.tags)):
        assert isinstance(ifd.tags[i], dngTag)
        if ifd.tags[i].TagId == tag_id[0]:
            ifd.tags[i] = tag
    return ifd


def set_ifd(ifd: dngIFD, mainIFD: dngIFD):
    for i in range(len(mainIFD.tags)):
        tag = mainIFD.tags[i]
        if tag.subIFD is not None:
            for j in range(len(tag.subIFD)):
                if tag.subIFD[j].ori_offset == ifd.ori_offset:
                    tag.subIFD[j] = ifd
    return mainIFD

def get_int_tag_value(ifd: dngIFD, tag_id: tuple, endian='little'):
    try:
        tag = get_tag(ifd=ifd, tag_id=tag_id)[1]
        type = tag_id[1]
        byte_len = len(tag.Value)
        data = []
        for i in range(0, byte_len, type[1]):
            data.append(int.from_bytes(tag.Value[i: i + type[1]], byteorder=endian))
        return data
    except Exception as e:
        return None


def set_tag_value(value, ifd: dngIFD, tag_id: tuple):
    try:
        tag = get_tag(ifd=ifd, tag_id=tag_id)[1]
        tag.setValue(value)
        set_tag(tag, ifd, tag_id)
        return ifd
    except Exception as e:
        raise e


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
                tile_ = np.frombuffer(data, dtype=dtype)
                tile_.reshape(w, h)
            tiles.append(tile_)

        tiles = np.array(tiles).reshape(n_h, n_w, h, w)
        tiles = tiles.transpose(0, 2, 1, 3).reshape(n_h * h, n_w * w)
        return tiles
    except:
        raise NotImplemented(f'Load tiles failed, compression type: {compression}')


def write_tile(data, tile: dngTile, ImageWidth=0, ImageLength=0, compression=1, dtype=np.uint16):
    try:
        assert compression == 7 or compression == 34892 or compression == 1
        tile_datas = []
        tile_bytecnts = []
        w = tile.tileWidth[0]
        h = tile.tileLength[0]

        n_h = int(np.ceil(ImageLength / h)) if int(np.ceil(ImageLength / h)) != 0 else 1
        n_w = int(np.ceil(ImageWidth / w)) if int(np.ceil(ImageWidth / w)) != 0 else 1

        # reshape data
        data = data.reshape(n_h, h, n_w, w).transpose(0, 2, 1, 3).reshape(-1, h, w)

        # data to bytes
        for i in range(data.shape[0]):
            if compression == 7 or compression == 34892:
                # 'rows', 'columns', 'samples_per_pixel', 'bits_allocated', 'bits_stored', 'pixel_representation', 'photometric_interpretation', 'number_of_frames'
                tile_data = RLELosslessEncoder.encode(data[i, ...])
                raise NotImplemented('Compression not implemented')
            elif compression == 1:
                tile_data = data[i, ...].flatten().astype(dtype).tobytes()
                tile_datas.append(tile_data)
                tile_bytecnts.append(len(tile_data))

        tile.data = tile_datas
        tile.byteCounts = tile_bytecnts

        return tile
    except Exception as e:
        raise Exception(f'Load tiles failed {e}, compression type: {compression}')

def get_dtype(bitspersample, reverse=False):
    if not reverse:
        if bitspersample == 16:
            return np.uint16
        if bitspersample == 8:
            return np.uint8
    else:
        if bitspersample == np.uint16:
            return 16
        if bitspersample == np.uint8:
            return 8

class DNGEditor(object):
    def __init__(self, DNG: smv_dng):
        self.dng = DNG
        self.endian = 'little' if self.dng.endian == '<' else 'big'
        self.CFA_IFD = None
        self.logger = logging.getLogger('DNGEditor')

    def extract_CFA(self, retrunCFAarray=True):
        CFA_IFD = None
        # travers IFDs

        for NewSubfileType in get_tags(ifd=self.dng.mainIFD, tag_id=Tag.NewSubfileType):
            # print(tag.TagId, tag.Value.decode())
            ifd, tag = NewSubfileType

            flag_full_res = False
            flag_cfa = False

            assert isinstance(tag, dngTag)
            if int.from_bytes(tag.Value[:Tag.NewSubfileType[1][1]], byteorder=self.endian) == 0:
                # full-resolution-image
                flag_full_res = True

            if get_int_tag_value(ifd=ifd, tag_id=Tag.PhotometricInterpretation)[0] == 32803:
                flag_cfa = True

            if flag_full_res and flag_cfa:
                CFA_IFD = ifd

        if CFA_IFD is None:
            raise Exception('CFA IFD not found.')

        if not retrunCFAarray:
            return

        # load IFD param
        self.CFA_IFD = CFA_IFD
        self.logger.debug(f'Load CFA_IFD, IFD offset: {self.CFA_IFD.ori_offset}')

        Compression = get_int_tag_value(ifd=self.CFA_IFD, tag_id=Tag.Compression, endian=self.endian)[0]
        ImageWidth = get_int_tag_value(ifd=self.CFA_IFD, tag_id=Tag.ImageWidth, endian=self.endian)[0]
        ImageLength = get_int_tag_value(ifd=self.CFA_IFD, tag_id=Tag.ImageLength, endian=self.endian)[0]
        BitsPerSample = get_int_tag_value(ifd=self.CFA_IFD, tag_id=Tag.BitsPerSample, endian=self.endian)[0]

        # load Tile param
        ActiveArea = get_int_tag_value(ifd=self.CFA_IFD, tag_id=Tag.ActiveArea, endian=self.endian)

        tile_data = load_tile(self.dng.IFDTiles[self.CFA_IFD.ori_offset], ImageWidth, ImageLength, Compression,
                              dtype=get_dtype(BitsPerSample))

        if ActiveArea is not None:
            active_tile = tile_data[ActiveArea[0]:ActiveArea[2], ActiveArea[1]:ActiveArea[3]]
        else:
            active_tile = tile_data

        self.logger.info(f'Load Tile {self.CFA_IFD.ori_offset}, tile size: {tile_data.shape}; Compression: {Compression}')
        self.logger.info(f'ActiveArea: {ActiveArea}, activeArea shape: {active_tile.shape}')

        return active_tile

    def write_CFA(self, data=None, compression=1):
        # try:
        #     assert compression == 1
        # except:
        #     raise NotImplemented('Available compression mode: 1')

        if self.CFA_IFD is None:
            self.extract_CFA(retrunCFAarray=False)

        Compression = get_int_tag_value(ifd=self.CFA_IFD, tag_id=Tag.Compression, endian=self.endian)[0]
        ImageWidth = get_int_tag_value(ifd=self.CFA_IFD, tag_id=Tag.ImageWidth, endian=self.endian)[0]
        ImageLength = get_int_tag_value(ifd=self.CFA_IFD, tag_id=Tag.ImageLength, endian=self.endian)[0]
        BitsPerSample = get_int_tag_value(ifd=self.CFA_IFD, tag_id=Tag.BitsPerSample, endian=self.endian)[0]

        # load Tile param
        ActiveArea = get_int_tag_value(ifd=self.CFA_IFD, tag_id=Tag.ActiveArea, endian=self.endian)

        tile_data = load_tile(self.dng.IFDTiles[self.CFA_IFD.ori_offset], ImageWidth, ImageLength, Compression,
                              dtype=get_dtype(BitsPerSample))

        if ActiveArea is not None:
            assert data.shape == tile_data[ActiveArea[0]:ActiveArea[2], ActiveArea[1]:ActiveArea[3]].shape
            tile_data[ActiveArea[0]:ActiveArea[2], ActiveArea[1]:ActiveArea[3]] = data
        else:
            assert data.shape == tile_data.shape
            tile_data = data

        # Overwrite tile data
        # Set compression
        set_tag_value([compression], self.CFA_IFD, Tag.Compression)
        self.dng.IFDTiles[self.CFA_IFD.ori_offset] = write_tile(tile_data, self.dng.IFDTiles[self.CFA_IFD.ori_offset],
                                                                ImageWidth, ImageLength, compression, dtype=get_dtype(BitsPerSample))
        self.logger.info(f'Overwrite IFDTile: {self.CFA_IFD.ori_offset}, Compression: {compression}')

        # Overwrite CFA_IFD
        self.dng.mainIFD = set_ifd(self.CFA_IFD, self.dng.mainIFD)
        self.logger.info(f'Overwrite IFD: {self.CFA_IFD.ori_offset}')


    def write(self, path):
        self.dng.write(path)
        self.logger.info(f'Write dng to: {path}')

