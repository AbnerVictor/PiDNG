from utils import Type, Tag, dngHeader, dngIFD, dngTag, DNG, tagId2tagType
from isp.pipeline_utils import get_metadata, get_image_ifds, get_image_tags
from isp.exif_utils import Ifd, Tag
from isp.exif_data_formats import exif_formats
import exifread
from exifread.tags import FIELD_TYPES, EXIF_TAGS
import struct

exiftype2dngTagtype = {
    1: Type.Byte,
    2: Type.Ascii,
    3: Type.Short,
    4: Type.Long,
    5: Type.Rational,
    6: Type.Sbyte,
    7: Type.Undefined,
    8: Type.Sshort,
    9: Type.Slong,
    10: Type.Srational,
    11: Type.Float,
    12: Type.Double
}


class smv_dng(object):
    def __init__(self, path):
        # read dng headers
        self.endian, self.IFDoffsets = self.read_header(path)

        # load IFDs
        self.IFDs = get_image_ifds(path)
        print(self.IFDs.keys())
        self.mainIFD = self.Ifd2dngIFD(self.IFDs[self.IFDoffsets[0]])

    def read_header(self, path):
        with open(path, 'rb') as binary:

            # Read endian
            binary.seek(0)
            b0 = binary.read(1)
            _ = binary.read(1)
            # byte storage direction (endian):
            # +1: b'M' (big-endian/Motorola)
            # -1: b'I' (little-endian/Intel)
            # endian = 1 if b0 == b'M' else -1
            # print("Endian = {}".format(b0))
            endian_sign = "<" if b0 == b'I' else ">"  # used in struct.unpack
            # print("Endian sign = {}".format(endian_sign))

            # Version
            _ = binary.read(2)  # 0x002A

            # offset to first IFD
            b4_7 = binary.read(4)  # offset to first IFD
            ifd_offsets = struct.unpack(endian_sign + "I", b4_7)

        return endian_sign, ifd_offsets

    def Tag2dngTag(self, tag: Tag):
        try:
            dtype = exiftype2dngTagtype[tag.data_format]
            if tag.tag_num == 330 or tag.tag_num == 34665:
                dtype = Type.IFD
        except Exception as e:
            return None

        value = tag.values

        if dtype == Type.Ascii:
            value = b''.join(tag.values).decode()
        if dtype == Type.Rational or dtype == Type.Srational:
            value = []
            for i in tag.values:
                value.append([i.numerator, i.denominator])

        dngtag = dngTag((tag.tag_num, dtype), value)

        dngtag.TagOffset = tag.offset

        if tag.tag_num == 330 or tag.tag_num == 34665:
            subIFD_ids = tag.values
            dngtag.subIFD = []
            for i in range(len(subIFD_ids)):
                offset = subIFD_ids[i]
                dngtag.subIFD.append(self.Ifd2dngIFD(self.IFDs[offset]))
        return dngtag

    def Ifd2dngIFD(self, ifd: Ifd):
        IFD = dngIFD()

        for tagID, tag in ifd.tags.items():
            dngtag = self.Tag2dngTag(tag)
            IFD.tags.append(dngtag)
        return IFD

    def write(self, path):
        dngTemplate = DNG()
        with open(path, 'wb') as binary:
            dngTemplate.IFDs.append(self.mainIFD)
            totalLength = dngTemplate.dataLen()
            buf = bytearray(totalLength)
            dngTemplate.setBuffer(buf)
            dngTemplate.write()
            binary.write(buf)


if __name__ == '__main__':
    dng_path = '../extras/IMG_4155.dng'
    # dng_path = '../extras/IMG_4155_dummy.dng'
    my_dng = smv_dng(dng_path)
    my_dng.write('../extras/IMG_4155_dummy.dng')
