import asyncio
from pydngconverter import DNGConverter, flags
import os
os.environ['PYDNG_DNG_CONVERTER'] = r'C:\Program Files\Adobe\Adobe DNG Converter'

path = r'\\192.168.100.201\Media-Dev\Experiment_Log\xin.yang\Experiment_backup\DNG_RAW\validate'

async def main():
    # Create converter instance.
    pydng = DNGConverter(source=path,
                        dest=os.path.join(path, 'results'),
                        jpeg_preview=flags.JPEGPreview.NONE,
                        fast_load=True,
                        )
    # Convert all
    return await pydng.convert()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()

# https://github.com/BradenM/pydngconverter