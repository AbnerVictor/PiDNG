from DNG.utils import Type, Tag, dngHeader, dngIFD, dngTag, dngStrip, dngTile, DNG
from DNG.exif_utils import Ifd, Tag, parse_exif
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

def get_image_ifds(image_path, verbose=False):
    ifds = parse_exif(image_path, verbose=verbose)
    return ifds


class smv_dng(object):
    def __init__(self, path, verbose=False):
        # read dng headers
        self.endian, self.IFDoffsets = self.read_header(path)
        self.IFDStrips = {}
        self.IFDTiles = {}

        # load IFDs
        self.IFDs = get_image_ifds(path, verbose=verbose)
        self.mainIFD = self.Ifd2dngIFD(self.IFDs[self.IFDoffsets[0]])

        # load data Stripes
        self.load_strips(path)

        # load data Tiles
        self.load_tiles(path)

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
            endian_sign = "<" if b0 == b'I' else ">"  # used in struct.unpack

            # Version
            _ = binary.read(2)  # 0x002A

            # offset to first IFD
            b4_7 = binary.read(4)  # offset to first IFD
            ifd_offsets = struct.unpack(endian_sign + "I", b4_7)

        return endian_sign, ifd_offsets

    def load_strips(self, path):
        with open(path, 'rb') as binary:
            for key, val in self.IFDStrips.items():
                assert isinstance(val, dngStrip)
                # load strip
                for i in range(val.stripCount()):
                    binary.seek(val.offset[i])
                    val.data.append(binary.read(val.byteCounts[i]))

    def load_tiles(self, path):
        with open(path, 'rb') as binary:
            for key, val in self.IFDTiles.items():
                assert isinstance(val, dngTile)
                # load strip
                for i in range(val.tileCount()):
                    binary.seek(val.offset[i])
                    val.data.append(binary.read(val.byteCounts[i]))

    def Tag2dngTag(self, tag: Tag, ifd: Ifd):
        try:
            dtype = exiftype2dngTagtype[tag.data_format]
            if tag.tag_num == 330 or tag.tag_num == 34665:
                dtype = Type.IFD
        except Exception as e:
            return None

        value = tag.values

        if dtype == Type.Ascii:
            value = b''.join(tag.values).decode().strip(b'\x00'.decode())
        if dtype == Type.Rational or dtype == Type.Srational:
            value = []
            for i in tag.values:
                value.append([i.numerator, i.denominator])

        dngtag = dngTag((tag.tag_num, dtype), value)

        dngtag.TagOffset = tag.offset

        # load subIFDs
        if tag.tag_num == 330 or tag.tag_num == 34665:
            subIFD_ids = tag.values
            dngtag.subIFD = []
            for i in range(len(subIFD_ids)):
                offset = subIFD_ids[i]
                dngtag.subIFD.append(self.Ifd2dngIFD(self.IFDs[offset]))


        # load strips
        if tag.tag_num == 273 or tag.tag_num == 278 or tag.tag_num == 279:
            if tag.tag_num == 273:
                # StripOffsets
                strip = dngStrip(ifd.offset, tag.values)
            else:
                strip = self.IFDStrips[ifd.offset]
            if tag.tag_num == 278:
                # RowsPerStrip
                strip.rowPerStrip = tag.values[0]
            if tag.tag_num == 279:
                # StripByteCounts
                strip.byteCounts = tag.values

            self.IFDStrips[ifd.offset] = strip

        # load Tiles
        if tag.tag_num == 322 or tag.tag_num == 323 \
            or tag.tag_num == 324 or tag.tag_num == 325:
            if ifd.offset not in self.IFDTiles.keys():
                tile = dngTile(ifd.offset)
            else:
                tile = self.IFDTiles[ifd.offset]
            if tag.tag_num == 322:
                # TileWidth
                tile.tileWidth = tag.values
            if tag.tag_num == 323:
                # TileLength
                tile.tileLength = tag.values
            if tag.tag_num == 324:
                # TileOffsets
                tile.offset = tag.values
            if tag.tag_num == 325:
                # TileByteCounts
                tile.byteCounts = tag.values
                pass
            self.IFDTiles[ifd.offset] = tile
        return dngtag

    def Ifd2dngIFD(self, ifd: Ifd):
        IFD = dngIFD()
        IFD.ori_offset = ifd.offset
        for tagID, tag in sorted(ifd.tags.items(), key=lambda x: x[0]):
            dngtag = self.Tag2dngTag(tag, ifd)
            IFD.tags.append(dngtag)
        return IFD

    def write(self, path):
        dngTemplate = DNG()
        with open(path, 'wb') as binary:
            # load IFD
            dngTemplate.IFDs.append(self.mainIFD)

            # load Strips
            for key, val in self.IFDStrips.items():
                dngTemplate.ImageDataStrips.append(val)

            # load Tiles
            for key, val in self.IFDTiles.items():
                dngTemplate.ImageTiles.append(val)

            totalLength = dngTemplate.dataLen()
            buf = bytearray(totalLength)
            dngTemplate.setBuffer(buf)
            dngTemplate.write()
            binary.write(buf)


if __name__ == '__main__':
    # dng_path = '../extras/IMG_4155.dng'
    # dng_path = '../extras/IMG_4155_dummy.dng'
    dng_path = '../extras/raw_deblur/M03-1318_000065.dng'
    my_dng = smv_dng(dng_path)
    my_dng.write('../extras/raw_deblur/M03-1318_000065_dummy.dng')
