from DNG.dng import smv_dng
from DNG.utils import dngTag, dngIFD, dngTile, dngStrip, Tag
import struct


def get_tags(ifd: dngIFD, tag_id: tuple):
    for tag in ifd.tags:
        assert isinstance(tag, dngTag)
        if tag.TagId == tag_id[0]:
            yield (ifd, tag)

        if tag.subIFD is not None:
            for sub_ifd in tag.subIFD:
                for tag_ in get_tags(sub_ifd, tag_id):
                    yield tag_


def get_int_tag_value(ifd: dngIFD, tag_id: tuple, endian='<'):
    try:
        tag = get_tags(ifd=ifd, tag_id=tag_id).__next__()[1]
        return int.from_bytes(tag.Value, byteorder='little' if endian == '<' else '>')
    except Exception as e:
        return None


class DNGEditor(object):
    def __init__(self, DNG: smv_dng):
        self.dng = DNG

    def extract_CFA(self):
        CFA_IFD = None
        # travers IFDs
        for NewSubfileType in get_tags(ifd=self.dng.mainIFD, tag_id=Tag.NewSubfileType):
            # print(tag.TagId, tag.Value.decode())
            ifd, tag = NewSubfileType

            flag_full_res = False
            flag_cfa = False

            assert isinstance(tag, dngTag)
            if tag.Value[0] == 0:
                # full-resolution-image
                flag_full_res = True

            if get_int_tag_value(ifd=ifd, tag_id=Tag.PhotometricInterpretation) == 32803:
                flag_cfa = True


            if flag_full_res and flag_cfa:
                CFA_IFD = ifd

        if CFA_IFD is None:
            raise Exception('CFA IFD not found.')

        # load IFD param
        Compression = get_int_tag_value(ifd=CFA_IFD, tag_id=Tag.Compression)
        ImageWidth = get_int_tag_value(ifd=CFA_IFD, tag_id=Tag.ImageWidth)
        ImageLength = get_int_tag_value(ifd=CFA_IFD, tag_id=Tag.ImageLength)

        # load Tile param
        TileWidth = get_int_tag_value(ifd=CFA_IFD, tag_id=Tag.TileWidth)
        TileLength = get_int_tag_value(ifd=CFA_IFD, tag_id=Tag.TileLength)
        DefaultCropSize = get_int_tag_value(ifd=CFA_IFD, tag_id=Tag.DefaultCropSize)
        DefaultCropOrigin = get_int_tag_value(ifd=CFA_IFD, tag_id=Tag.DefaultCropOrigin)


if __name__ == '__main__':
    import os

    root = r'C:\Users\abner.yang\Downloads\raw_4097'
    name = 'IMG_4097'
    raw_pth = os.path.join(root, name + '.dng')
    dng_file = smv_dng(raw_pth, verbose=False)

    my_dng = DNGEditor(dng_file)
    my_dng.extract_CFA()
