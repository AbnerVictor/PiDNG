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

## Editing DNG

```python
from DNG.Editor import DNGEditor
from DNG.dng import smv_dng
import logging

import os
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)

root = r'C:\Users\abner.yang\Downloads\raw_4097'
name = 'DSC_2849'

# input dng path
raw_pth = os.path.join(root, name + '.dng')

# output dng path
out_pth = os.path.join(root, name + '_mod' + '.dng')

# Step 1: Load DNG file
dng_file = smv_dng(raw_pth, verbose=False)

# Step 2: initialize DNGEditor
my_dng = DNGEditor(dng_file)

# Step 3: extract CFA
active_tile = my_dng.extract_CFA()
# Noted that the 'active_tile' is usually a 2D grayscale image

# Step 4: your application
# denoising, deblurring ...
# e.g. output = net(active_tile)
output = active_tile

# Step 5: Overwrite CFA
my_dng.write_CFA(output, compression=1)
# compression = 1 means no compression, 
# currently, only compression == 1 is supported
# Please click link below for more details: 
# https://www.awaresystems.be/imaging/tiff/tifftags/compression.html

# Step 6: Write DNG
my_dng.write(out_pth)
```

## Load Tags

```python
from DNG.Editor import DNGEditor, get_int_tag_value
from DNG.dng import smv_dng
from DNG.utils import Tag

import os

root = r'C:\Users\abner.yang\Downloads\raw_4097'
name = 'DSC_2849'

# input dng path
raw_pth = os.path.join(root, name + '.dng')

dng_file = smv_dng(raw_pth, verbose=False)
my_dng = DNGEditor(dng_file)

# For example, we need to load black level of CFA
# Step 1: Extract CFA
active_tile = my_dng.extract_CFA()

BlackLevel = get_int_tag_value(my_dng.CFA_IFD, tag_id=Tag.BlackLevel, endian=my_dng.endian)
print(BlackLevel)
```