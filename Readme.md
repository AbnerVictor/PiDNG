# DNG Utility

## Read and write

### Load IFDs, Tags, Strips and Tiles

Read DNG file

```python
from DNG.dng import smv_dng

# LOAD DNG
my_dng = smv_dng('dummy.dng', verbose=True)
# print tags when verbose = True
```

- IFDs
    - Tags
- IFD_Strips
    - IFD offset
    - DNGStrip
- IFD_Tiles
    - IFD offset
    - DNGTile

### Write IFDs, Tags, Strips and Tiles

Write DNG file

```python
my_dng.write('new_dummy.dng')
```

## Decode and Encode

原本的DNG里面的CFA提取出来 -> 处理 -> 替换回去
算法处理输出的结果 -> 原本的数据结构是相同的

统一输入输出规范
- 是否压缩
- 需要什么数据
  - raw -> RGBG array (4-chan) -> network -> RGBG array (4-chan)
- 格式

TODO:

- read CFA (checked)
- crop CFA (tbd)
- write CFA (compression tbd)
