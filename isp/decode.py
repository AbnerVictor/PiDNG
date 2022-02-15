import glob
import os
import sys
import imageio
import imageio_ffmpeg
import numpy as np
dirs = os.listdir('./')[3:]
for dir in dirs:
    dir = './' + dir
    files = glob.glob(dir + '/*.mov')[1:]
    for file in files:
        input_name = file
        rgb_path = os.path.join(dir, os.path.basename(file)[17:21] + '_rgb')
        yuv_path = os.path.join(dir, os.path.basename(file)[17:21] + '_yuv')
        if not os.path.exists(rgb_path):
            os.mkdir(rgb_path)
        if not os.path.exists(yuv_path):
            os.mkdir(yuv_path)
        bash = 'ffmpeg -i {} {}/img_%5d.png'.format(input_name, rgb_path)
        os.system(bash)
        if 'fcp' not in file:
            output_name = input_name.replace('.MOV', '.yuv')
            bash = bash = 'ffmpeg -i {} -c:v rawvideo -pix_fmt yuv420p {}'.format(input_name, output_name)
            os.system(bash)

            reader = imageio.get_reader(input_name, 'ffmpeg')
            meta = reader.get_meta_data()
            nframe = int(reader.count_frames())
            width, height = 1920, 1080
            length = int(width * height)

            f = open(output_name, 'rb')

            for i in range(nframe):
                frame = np.frombuffer(f.read(int(length * 1.5)), dtype=np.uint8)
                f.seek(int((i + 1) * length * 1.5))
                #if i % 2 == 0:
                y = frame[:width * height].reshape(height, width)
                u = frame[int(width * height):int(1.25 * width * height)].reshape(int(height / 2), int(width / 2))
                v = frame[int(1.25 * width * height):int(1.5 * width * height)].reshape(int(height / 2),int(width / 2))
                imageio.imwrite('{}/{}_y.png'.format(yuv_path, i), y)
                imageio.imwrite('{}/{}_u.png'.format(yuv_path, i), u)
                imageio.imwrite('{}/{}_v.png'.format(yuv_path, i), v)
                # else:
                #     y = frame[:width * height].reshape(height, width)
                #     u = frame[int(width * height):int(1.25 * width * height)].reshape(int(height / 2), int(width / 2))
                #     v = frame[int(1.25 * width * height):int(1.5 * width * height)].reshape(int(height / 2),
                #                                                                             int(width / 2))
                #     y_y, u_u, v_v = y.copy(), u.copy(), v.copy()
                #     u_1 = u[0:int(height / 2):2, :]
                #     u_2 = u[1:int(height / 2):2, :]
                #     v_1 = v[0:int(height / 2):2, :]
                #     v_2 = v[1:int(height / 2):2, :]
                #     # v_v[0:int(height/2):2, :], v_v[1:int(height/2):2, :] = u[0:int(height/2):2, :], v[1:int(height/2):2, :]
                #
                #     y_y[:int(height / 4), :] = y[int(height / 4 * 3):, :]
                #     y_y[int(height / 4 * 3):, :] = y[:int(height / 4), :]
                #
                #     y_y[int(height / 4):int(height / 4 * 2), :int(width / 2)] = u[0:int(height / 2):2, :]
                #     y_y[int(height / 4 * 2):int(height / 4 * 3), :int(width / 2)] = v[0:int(height / 2):2, :]
                #
                #     y_y[int(height / 4):int(height / 4 * 2), int(width / 2):] = u[1:int(height / 2):2, :]
                #     y_y[int(height / 4 * 2):int(height / 4 * 3), int(width / 2):] = v[1:int(height / 2):2, :]
                #
                #     u_u[0:int(height / 2):2, :] = y[int(height / 4):int(height / 4 * 2), :int(width / 2)]
                #     u_u[1:int(height / 2):2, :] = y[int(height / 4):int(height / 4 * 2), int(width / 2):]
                #
                #     v_v[0:int(height / 2):2, :] = y[int(height / 4 * 2):int(height / 4 * 3), :int(width / 2)]
                #     v_v[1:int(height / 2):2, :] = y[int(height / 4 * 2):int(height / 4 * 3), int(width / 2):]
                #
                #     imageio.imwrite('{}/{}_y.png'.format(yuv_path, i), y_y)
                #     imageio.imwrite('{}/{}_u.png'.format(yuv_path, i), u_u)
                #     imageio.imwrite('{}/{}_v.png'.format(yuv_path, i), v_v)
                #






