from pidng.dng import Type, Tag, dngHeader, dngIFD, dngTag, DNG
from isp.pipeline_utils import get_metadata, get_image_ifds, get_image_tags
from isp.exif_utils import Ifd, Tag
import exifread
from exifread.tags import FIELD_TYPES, EXIF_TAGS
import rawpy

FIELD_TYPES_2_Type = {
    FIELD_TYPES[0][2]: Type.Invalid,
    FIELD_TYPES[1][2]: Type.Byte,
    FIELD_TYPES[2][2]: Type.Ascii,
    FIELD_TYPES[3][2]: Type.Short,
    FIELD_TYPES[4][2]: Type.Long,
    FIELD_TYPES[5][2]: Type.Rational,
    FIELD_TYPES[6][2]: Type.Sbyte,
    FIELD_TYPES[7][2]: Type.Undefined,
    FIELD_TYPES[8][2]: Type.Sshort,
    FIELD_TYPES[9][2]: Type.Slong,
    FIELD_TYPES[10][2]: Type.Srational,
    FIELD_TYPES[11][2]: Type.Float,
    FIELD_TYPES[12][2]: Type.Double,
    FIELD_TYPES[13][2]: Type.IFD
}


class smv_dng(object):
    def __init__(self, path):
        self.mainIFD = self.__load_tags__(path)
        # self.subIFDs = self.__load_sub_ifds__(path)

    def __load_tags__(self, path=None, tags=None):
        ifd = dngIFD()
        if tags is None:
            with open(path, 'rb') as f:
                tags = exifread.process_file(f)
        for key, val in tags.items():
            assert isinstance(val, exifread.classes.IfdTag)

            # convert exifread tags to PiDNG tags
            tag = val.tag
            types = FIELD_TYPES_2_Type[FIELD_TYPES[val.field_type][2]]
            value = val.values

            offset = val.field_offset
            length = val.field_length

            # Ratio to list items
            if types == Type.Srational or types == Type.Rational:
                ratio_list = []
                for i in value:
                    if isinstance(i, exifread.utils.Ratio):
                        ratio_list.append([i.numerator, i.denominator])
                value = ratio_list
            if types == Type.Float or types == Type.Double:
                float_list = []
                for i in value:
                    if isinstance(i, tuple):
                        float_list.append(i[0])
                value = float_list

            print(tag, types, value, offset, length)
            ifd.tags.append(dngTag([tag, types], value))
        return ifd

    def write(self, path):
        dngTemplate = DNG()


if __name__ == '__main__':
    dng_path = '../extras/IMG_4155.dng'
    my_dng = smv_dng(dng_path)
    my_dng.write()