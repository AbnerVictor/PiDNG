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

class DNGEditor(object):
    def __init__(self, DNG: smv_dng):
        self.dng = DNG

    def extract_CFA(self):
        CFA_IFD = None
        # travers IFDs
        for res in get_tags(ifd=self.dng.mainIFD, tag_id=Tag.NewSubfileType):
            # print(tag.TagId, tag.Value.decode())
            ifd, tag = res
            assert isinstance(tag, dngTag)
            if tag.Value[0] == 0:
                # full-resolution-image
                
                pass


if __name__ == '__main__':
    import os

    root = r'C:\Users\abner.yang\Downloads\raw_4097'
    name = 'IMG_4097'
    raw_pth = os.path.join(root, name+'.dng')
    dng_file = smv_dng(raw_pth, verbose=False)

    my_dng = DNGEditor(dng_file)
    my_dng.extract_CFA()