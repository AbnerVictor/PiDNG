# DNG Utility

## Read and write

### Load IFDs, Tags, Strips and Tiles

Read DNG file

```python
    from DNG.DNG import smv_dng
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

