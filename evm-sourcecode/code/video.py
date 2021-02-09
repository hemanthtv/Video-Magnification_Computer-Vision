#..................................
#........Visualisierung 2..........
#..................................
#...Eulerian Video Magnification...
#..................................
#.. Author: Galya Pavlova..........
#..................................

import numpy as np
import cv2
import platform


def load_video(vidFile):
    '''
    Reads the video
    :param vidFile: Video file
    :return: video sequence, frame rate, width & height of video frames
    '''
    print('Load video')
    vid = cv2.VideoCapture(vidFile)
    fr = vid.get(cv2.CAP_PROP_FPS)  # frame rate
    len = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    vidWidth = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    vidHeight = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # save video as stack of images
    video_stack = np.empty((len, vidHeight, vidWidth, 3))

    for x in range(len):
        ret, frame = vid.read()

        video_stack[x] = frame

    vid.release()

    return video_stack, fr, vidWidth, vidHeight


def save_video(video_tensor, fps, name):
    '''
    Creates a new video for the output
    :param video_tensor: filtered video sequence
    :param fps: frame rate of original video
    :param name: output video name
    '''
    print('Save video')
    if platform.system()=='Linux':
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    else:
        fourcc = cv2.VideoWriter_fourcc(*'PIM1')
    [height, width] = video_tensor[0].shape[0:2]
    writer = cv2.VideoWriter(name+"Out.avi", fourcc, fps, (width, height), 1)
    for i in range(video_tensor.shape[0]):
        writer.write(cv2.convertScaleAbs(video_tensor[i]))
    writer.release()


def calculate_pyramid_levels(vidWidth, vidHeight):
    '''
    Calculates the maximal pyramid levels for the Laplacian pyramid
    :param vidWidth: video frames' width
    :param vidHeight: video frames' height
    '''
    if vidWidth < vidHeight:
        levels = int(np.log2(vidWidth))
    else:
        levels = int(np.log2(vidHeight))

    return levels


def rgb2yiq(video):
    '''
    Converts the video color from RGB to YIQ (NTSC)
    :param video: RGB video sequence
    :return: YIQ-color video sequence
    '''
    yiq_from_rgb = np.array([[0.299, 0.587, 0.114],
                             [0.596, -0.274, -0.322],
                             [0.211, -0.523, 0.312]])
    t = np.dot(video, yiq_from_rgb.T)
    return t


def yiq2rgb(video):
    '''
    Converts the video color from YIQ (NTSC) to RGB
    :param video: YIQ-color video sequence
    :return: RGB video sequence
    '''
    rgb_from_yiq = np.array([[1, 0.956, 0.621],
                             [1, -0.272, -0.647],
                             [1, -1.106, 1.703]])
    t = np.dot(video, rgb_from_yiq.T)
    return t
