import numpy as np
from pipeline_utils import get_visible_raw_image, get_metadata, normalize, white_balance, demosaic, apply_lens_correction, apply_hue_correction, apply_exposure_compensation, \
    apply_hsv_enhance, apply_color_space_transform, transform_xyz_to_srgb, transform_xyz_to_prorgb, apply_brighten, apply_gamma, apply_tone_map, fix_orientation, transform_prorgb_to_srgb, raw_rgb_to_cct, \
    transform_rgb_to_raw, apply_degamma, de_white_balance, apply_mosaic, add_noise, add_caliberate_noise, add_gray_noise, crop
from matplotlib import pyplot as plt
import imageio
from bm3d import bm3d
import colour
import cv2
from cv2.ximgproc import guidedFilter
def inverse_pipeline(image, meta_path, ratio, noise_profile, middle_ratio, low_ratio, add = False):
    metadata = get_metadata(meta_path)
    img = image / 255.0

    degamma_image = apply_degamma(img)

    temp = raw_rgb_to_cct(metadata)
    rawrgb_image = transform_rgb_to_raw(degamma_image, temp, metadata)

    de_white_balance_image = de_white_balance(rawrgb_image, metadata['as_shot_neutral'])

    raw_image = apply_mosaic(de_white_balance_image)
    if add:

        raw_image, shot, read = add_noise(raw_image, noise_profile, metadata['as_shot_neutral'], ratio,
                                                   middle_ratio, low_ratio)
        return raw_image, shot, read
    return raw_image, None




def run_pipeline_v2(image_or_path, params=None, metadata=None, fix_orient=True):
    params_ = params.copy()
    if type(image_or_path) == str:
        image_path = image_or_path
        # raw image data
        raw_image = get_visible_raw_image(image_path)
        # metadata
        metadata = get_metadata(image_path)
    else:
        raw_image = image_or_path.copy()
        # must provide metadata
        if metadata is None:
            raise ValueError("Must provide metadata when providing image data in first argument.")

    current_stage = 'raw'
    current_image = raw_image

    if params_['input_stage'] == current_stage:
        # linearization
        linearization_table = metadata['linearization_table']
        if linearization_table is not None:
            print('Linearization table found. Not handled.')
            # TODO

        current_image = normalize(current_image, metadata['black_level'], metadata['white_level'])
        params_['input_stage'] = 'normal'

    current_stage = 'normal'

    if params_['output_stage'] == current_stage:
        return current_image

    if params_['input_stage'] == current_stage:
        current_image = white_balance(current_image, metadata['as_shot_neutral'], metadata['cfa_pattern'])
        params_['input_stage'] = 'white_balance'

    current_stage = 'white_balance'

    if params_['output_stage'] == current_stage:
        return current_image

    if params_['input_stage'] == current_stage:
        current_image = demosaic(current_image, metadata['cfa_pattern'], output_channel_order='BGR',
                                 alg_type=params_['demosaic_type'])
        params_['input_stage'] = 'demosaic'

    current_stage = 'demosaic'

    if params_['output_stage'] == current_stage:
        return current_image

    if params_['input_stage'] == current_stage:
        current_image = apply_color_space_transform(current_image, metadata['color_matrix_1'],
                                                    metadata['color_matrix_2'])
        params_['input_stage'] = 'xyz'

    current_stage = 'xyz'

    if params_['output_stage'] == current_stage:
        return current_image

    if params_['input_stage'] == current_stage:
        current_image = transform_xyz_to_srgb(current_image)
        params_['input_stage'] = 'srgb'

    current_stage = 'srgb'

    if fix_orient:
        # fix image orientation, if needed (after srgb stage, ok?)
        current_image = fix_orientation(current_image, metadata['orientation'])

    if params_['output_stage'] == current_stage:
        return current_image

    if params_['input_stage'] == current_stage:
        current_image = apply_gamma(current_image)
        params_['input_stage'] = 'gamma'

    current_stage = 'gamma'

    if params_['output_stage'] == current_stage:
        return current_image

    if params_['input_stage'] == current_stage:
        current_image = apply_tone_map(current_image)
        params_['input_stage'] = 'tone'

    current_stage = 'tone'

    if params_['output_stage'] == current_stage:
        return current_image

    # invalid input/output stage!
    raise ValueError('Invalid input/output stage: input_stage = {}, output_stage = {}'.format(params_['input_stage'],
                                                                                              params_['output_stage']))


def run_pipeline(image_path, params, tone_fn):

    # metadata

    raw_image = get_visible_raw_image(image_path)
    # metadata
    metadata = get_metadata(image_path)



    ##################  linearization  ###########################################################################
    linearization_table = metadata['linearization_table']
    if linearization_table is not None:
        print('Linearization table found. Not handled.')
        # TODO

    normalized_image = normalize(raw_image, metadata['black_level'], metadata['white_level'])
    normalized_image = crop(normalized_image, metadata['crop_region'], metadata['crop_size'])
    if params['output_stage'] == 'normal':
        return normalized_image
    ##############################################################################################################

    ##################  demosaicing  #############################################################################
    demosaiced_image = demosaic(normalized_image, metadata['white_level'], metadata['cfa_pattern'], output_channel_order='BGR',
                                alg_type=params['demosaic_type'] )
    # fix image orientation, if needed
    demosaiced_image = fix_orientation(demosaiced_image, metadata['orientation'])
    if params['output_stage'] == 'demosaic':
        return demosaiced_image
    ##############################################################################################################



    ##################  white_balance  ###########################################################################
    white_balanced_image = white_balance(demosaiced_image, metadata['as_shot_neutral'])

    if params['output_stage'] == 'white_balance':
        return white_balanced_image
    ##############################################################################################################

    ##################  Denoise  ###########################################################################

    ########################################################################################################


    ##################  color_space_trans  #######################################################################
    temp = raw_rgb_to_cct(metadata)

    xyz_image = apply_color_space_transform(white_balanced_image, metadata, temp)

    if params['output_stage'] == 'xyz':
        return xyz_image


    # denoised_image = bm3d(xyz_image, 8 * np.sqrt(metadata['noise_profile'][1]))
    # yuv_img = colour.XYZ_to_Luv(denoised_image)
    # xyz_image = colour.XYZ_to_Luv(xyz_image)
    # xyz_image[:, :, 1:] = yuv_img[:, :, 1:]
    # xyz_image = colour.Luv_to_XYZ(xyz_image)


    prorgb_image = transform_xyz_to_prorgb(xyz_image)

    if params['output_stage'] == 'prorgb':
        return prorgb_image
    ##############################################################################################################




    ##################  hsv_correction  ##########################################################################
    # hue_corrected_image = apply_hue_correction(prorgb_image, metadata['hue_map1'], metadata['hue_map2'], temp)
    # if params['output_stage'] == 'hue':
    #     return hue_corrected_image
    ##############################################################################################################




    ##################  exposure_compensation  ###################################################################
    ev_image = apply_exposure_compensation(prorgb_image, metadata['base_exposure'])
    if params['output_stage'] == 'ev':
        return ev_image
    ##############################################################################################################




    # ##################  hsv_enhancement  #########################################################################
    # hsv_enhanced_image = apply_hsv_enhance(prorgb_image, metadata['hsv_map'])
    # if params['output_stage'] == 'hsv_enhance':
    #     return hsv_enhanced_image
    ##############################################################################################################




    ##################  tone_mapping  ############################################################################
    tone_mapped_image = apply_tone_map(ev_image, tone_fn)
    if params['output_stage'] == 'tone':
        return tone_mapped_image
    ##############################################################################################################




    ##################  color_trans & gamma_correction  ##########################################################
    srgb_image = transform_prorgb_to_srgb(tone_mapped_image)
    if params['output_stage'] == 'sRGB':
        return srgb_image
    gamma_corrected_image = apply_gamma(srgb_image)
    if params['output_stage'] == 'gamma':
        return gamma_corrected_image

    yuv_img = colour.RGB_to_YCbCr(gamma_corrected_image).astype(np.float32)


    yuv_img[:, :, 1] = guidedFilter(yuv_img[:, :, 0], yuv_img[:, :, 1], radius = 12, eps = 30)
    yuv_img[:, :, 2] = guidedFilter(yuv_img[:, :, 0], yuv_img[:, :, 2], radius = 12, eps = 30)
    denoise_img = np.clip(colour.YCbCr_to_RGB(yuv_img), 0, 1)
    if params['output_stage'] == 'denoise':
        return denoise_img
    ##############################################################################################################




    ##################  vignetting_correction  ###################################################################
    lens_corrected_image = apply_lens_correction(gamma_corrected_image)
    if params['output_stage'] == 'lens_correction':
        return lens_corrected_image
    ##############################################################################################################


    output_image = None
    return output_image





